"""
Main Telegram Music Bot
Uses ShazamIO for song recognition and supports multiple platforms for downloading
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Union

import telegram
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
    Message,
    Update,
    User,
    Audio,
    Video,
    Voice,
    VideoNote,
    Document,
    BotCommand,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)
from telegram.constants import ParseMode

from shazamio import Shazam
import yt_dlp
import instaloader
import requests
from mutagen import File as MutagenFile
from mutagen.id3 import ID3NoHeaderError

from config import BOT_MESSAGES, BOT_TOKEN, ADMIN_USER_ID, AUDIO_FORMATS, VIDEO_FORMATS
from services.song_recognizer import SongRecognizer
from services.downloader import Downloader
from services.firebase_service import FirebaseService
from utils.helpers import (
    format_duration,
    get_file_extension,
    clean_temp_files,
    is_admin,
    get_bot_ping,
)
from models.user import User
from models.song import Song

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Conversation states
EDIT_SONG_WAITING_FOR_FILE = 1
EDIT_SONG_WAITING_FOR_INFO = 2
BROADCAST_WAITING_FOR_MESSAGE = 3
BROADCAST_WAITING_FOR_DURATION = 4

class MusicBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.shazam = Shazam()
        self.song_recognizer = SongRecognizer(self.shazam)
        self.downloader = Downloader()
        self.firebase_service = FirebaseService()
        self.user_languages: Dict[int, str] = {}
        self.user_states: Dict[int, int] = {}
        
        # Initialize bot commands
        self._setup_commands()
        
    def _setup_commands(self):
        """Setup bot commands"""
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help"),
            BotCommand("statistics", "Show bot statistics"),
            BotCommand("language", "Change language"),
            BotCommand("broadcast", "Broadcast message (admin only)"),
        ]
        self.application.bot.set_my_commands(commands)
    
    def get_user_language(self, user_id: int) -> str:
        """Get user language, default to English"""
        return self.user_languages.get(user_id, 'en')
    
    def get_message(self, user_id: int, key: str, **kwargs) -> str:
        """Get localized message"""
        lang = self.get_user_language(user_id)
        message = BOT_MESSAGES[lang].get(key, BOT_MESSAGES['en'].get(key, key))
        return message.format(**kwargs)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        # Save user to Firebase
        await self.firebase_service.save_user(User(
            id=user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language=self.get_user_language(user_id),
            joined_at=datetime.now()
        ))
        
        # Create language selection keyboard
        keyboard = [
            [
                InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
                InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = self.get_message(user_id, 'welcome')
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_id = update.effective_user.id
        help_text = self.get_message(user_id, 'main_menu')
        
        keyboard = [
            [
                InlineKeyboardButton("🎵 Recognize Song", callback_data="recognize"),
                InlineKeyboardButton("🔗 Download from Link", callback_data="download_link"),
            ],
            [
                InlineKeyboardButton("✏️ Edit Song Info", callback_data="edit_song"),
                InlineKeyboardButton("📊 Statistics", callback_data="show_stats"),
            ],
            [
                InlineKeyboardButton("🌐 Change Language", callback_data="change_lang"),
                InlineKeyboardButton(self.get_message(user_id, 'back'), callback_data="main_menu"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    async def statistics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /statistics command"""
        user_id = update.effective_user.id
        
        # Get statistics from Firebase
        stats = await self.firebase_service.get_statistics()
        ping = get_bot_ping()
        
        stats_text = self.get_message(
            user_id, 'statistics',
            users=stats['total_users'],
            recognized=stats['songs_recognized'],
            downloaded=stats['songs_downloaded'],
            ping=ping
        )
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.HTML)
    
    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /language command"""
        user_id = update.effective_user.id
        
        keyboard = [
            [
                InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
                InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Choose your language / زبان خود را انتخاب کنید:",
            reply_markup=reply_markup
        )
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /broadcast command (admin only)"""
        user_id = update.effective_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text(self.get_message(user_id, 'admin_only'))
            return
        
        self.user_states[user_id] = BROADCAST_WAITING_FOR_MESSAGE
        await update.message.reply_text(self.get_message(user_id, 'broadcast'))
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        user_id = query.from_user.id
        data = query.data
        
        await query.answer()
        
        # Delete previous message
        try:
            await query.delete_message()
        except:
            pass
        
        if data.startswith('lang_'):
            # Language selection
            lang = data.split('_')[1]
            self.user_languages[user_id] = lang
            await self.firebase_service.update_user_language(user_id, lang)
            
            await query.message.reply_text(self.get_message(user_id, 'language_selected'))
            await self.help_command(update, context)
            
        elif data == 'main_menu':
            await self.help_command(update, context)
            
        elif data == 'recognize':
            await query.message.reply_text(self.get_message(user_id, 'send_audio'))
            
        elif data == 'download_link':
            await query.message.reply_text(self.get_message(user_id, 'send_link'))
            
        elif data == 'edit_song':
            self.user_states[user_id] = EDIT_SONG_WAITING_FOR_FILE
            await query.message.reply_text(self.get_message(user_id, 'edit_song'))
            
        elif data == 'show_stats':
            await self.statistics_command(update, context)
            
        elif data == 'change_lang':
            await self.language_command(update, context)
    
    async def handle_audio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle audio/voice/video messages"""
        user_id = update.effective_user.id
        message = update.message
        
        # Check if user is in edit mode
        if self.user_states.get(user_id) == EDIT_SONG_WAITING_FOR_FILE:
            self.user_states[user_id] = EDIT_SONG_WAITING_FOR_INFO
            context.user_data['edit_file_id'] = message.audio.file_id if message.audio else message.voice.file_id
            await message.reply_text(self.get_message(user_id, 'edit_info'))
            return
        
        # Send processing message
        processing_msg = await message.reply_text(self.get_message(user_id, 'processing'))
        
        try:
            # Download the audio file
            file = None
            if message.audio:
                file = await message.audio.get_file()
            elif message.voice:
                file = await message.voice.get_file()
            elif message.video:
                file = await message.video.get_file()
            elif message.video_note:
                file = await message.video_note.get_file()
            
            if not file:
                await processing_msg.edit_text(self.get_message(user_id, 'unsupported_format'))
                return
            
            # Download file to temporary location
            file_path = f"temp/{file.file_id}.mp3"
            await file.download_to_drive(file_path)
            
            # Recognize song
            await processing_msg.edit_text(self.get_message(user_id, 'recognizing'))
            
            song_info = await self.song_recognizer.recognize_song(file_path)
            
            if song_info:
                # Update statistics
                await self.firebase_service.increment_stat('songs_recognized')
                
                # Format song info
                duration = format_duration(song_info.get('duration', 0))
                song_text = self.get_message(
                    user_id, 'song_found',
                    title=song_info.get('title', 'Unknown'),
                    artist=song_info.get('artist', 'Unknown'),
                    album=song_info.get('album', 'Unknown'),
                    duration=duration
                )
                
                # Try to download and send the song
                try:
                    await processing_msg.edit_text(self.get_message(user_id, 'downloading'))
                    
                    downloaded_path = await self.downloader.download_song(
                        f"{song_info.get('artist', '')} {song_info.get('title', '')}"
                    )
                    
                    if downloaded_path:
                        with open(downloaded_path, 'rb') as audio_file:
                            await message.reply_audio(
                                audio_file,
                                caption=song_text,
                                parse_mode=ParseMode.HTML
                            )
                        
                        # Update statistics
                        await self.firebase_service.increment_stat('songs_downloaded')
                    else:
                        await message.reply_text(song_text, parse_mode=ParseMode.HTML)
                        
                except Exception as e:
                    logger.error(f"Error downloading song: {e}")
                    await message.reply_text(song_text, parse_mode=ParseMode.HTML)
            else:
                await processing_msg.edit_text(self.get_message(user_id, 'song_not_found'))
            
            # Clean up temporary file
            clean_temp_files(file_path)
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            await processing_msg.edit_text(self.get_message(user_id, 'error', error=str(e)))
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        text = update.message.text
        
        # Check if user is in edit mode
        if self.user_states.get(user_id) == EDIT_SONG_WAITING_FOR_INFO:
            await self.handle_song_edit(update, context)
            return
        
        # Check if user is in broadcast mode
        if self.user_states.get(user_id) == BROADCAST_WAITING_FOR_MESSAGE:
            context.user_data['broadcast_message'] = text
            self.user_states[user_id] = BROADCAST_WAITING_FOR_DURATION
            await update.message.reply_text("⏱️ Enter message duration in hours (or 0 for permanent):")
            return
        
        if self.user_states.get(user_id) == BROADCAST_WAITING_FOR_DURATION:
            await self.handle_broadcast(update, context)
            return
        
        # Check if it's a URL
        if any(platform in text.lower() for platform in ['youtube.com', 'youtu.be', 'instagram.com', 'tiktok.com', 'pinterest.com', 'soundcloud.com']):
            await self.handle_url_download(update, context)
    
    async def handle_song_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle song information editing"""
        user_id = update.effective_user.id
        text = update.message.text
        
        try:
            # Parse song information
            info = {}
            for line in text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip().lower()] = value.strip()
            
            # Get the file ID
            file_id = context.user_data.get('edit_file_id')
            if not file_id:
                await update.message.reply_text(self.get_message(user_id, 'error', error="File not found"))
                return
            
            # Here you would update the file metadata
            # For now, just confirm the edit
            await update.message.reply_text(self.get_message(user_id, 'info_updated'))
            
            # Reset user state
            self.user_states.pop(user_id, None)
            context.user_data.pop('edit_file_id', None)
            
        except Exception as e:
            logger.error(f"Error editing song: {e}")
            await update.message.reply_text(self.get_message(user_id, 'error', error=str(e)))
    
    async def handle_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle broadcast message"""
        user_id = update.effective_user.id
        text = update.message.text
        
        try:
            duration_hours = int(text)
            message = context.user_data.get('broadcast_message')
            
            if not message:
                await update.message.reply_text(self.get_message(user_id, 'error', error="Message not found"))
                return
            
            # Get all users
            users = await self.firebase_service.get_all_users()
            
            # Send broadcast
            sent_count = 0
            for user in users:
                try:
                    await context.bot.send_message(
                        chat_id=user.id,
                        text=f"📢 {message}"
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error sending broadcast to {user.id}: {e}")
            
            await update.message.reply_text(
                self.get_message(user_id, 'broadcast_sent', count=sent_count)
            )
            
            if duration_hours > 0:
                await update.message.reply_text(
                    self.get_message(user_id, 'broadcast_duration', hours=duration_hours)
                )
            
            # Reset user state
            self.user_states.pop(user_id, None)
            context.user_data.pop('broadcast_message', None)
            
        except Exception as e:
            logger.error(f"Error broadcasting: {e}")
            await update.message.reply_text(self.get_message(user_id, 'error', error=str(e)))
    
    async def handle_url_download(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle URL download"""
        user_id = update.effective_user.id
        url = update.message.text
        
        processing_msg = await update.message.reply_text(self.get_message(user_id, 'processing'))
        
        try:
            # Download from URL
            downloaded_path = await self.downloader.download_from_url(url)
            
            if downloaded_path:
                # Recognize song if it's audio
                if any(downloaded_path.endswith(ext) for ext in AUDIO_FORMATS):
                    await processing_msg.edit_text(self.get_message(user_id, 'recognizing'))
                    
                    song_info = await self.song_recognizer.recognize_song(downloaded_path)
                    
                    if song_info:
                        await self.firebase_service.increment_stat('songs_recognized')
                        
                        duration = format_duration(song_info.get('duration', 0))
                        song_text = self.get_message(
                            user_id, 'song_found',
                            title=song_info.get('title', 'Unknown'),
                            artist=song_info.get('artist', 'Unknown'),
                            album=song_info.get('album', 'Unknown'),
                            duration=duration
                        )
                        
                        with open(downloaded_path, 'rb') as audio_file:
                            await update.message.reply_audio(
                                audio_file,
                                caption=song_text,
                                parse_mode=ParseMode.HTML
                            )
                        
                        await self.firebase_service.increment_stat('songs_downloaded')
                    else:
                        with open(downloaded_path, 'rb') as file:
                            await update.message.reply_document(
                                document=file,
                                caption="✅ Downloaded successfully!"
                            )
                else:
                    # Send as document
                    with open(downloaded_path, 'rb') as file:
                        await update.message.reply_document(
                            document=file,
                            caption="✅ Downloaded successfully!"
                        )
                
                await processing_msg.edit_text(self.get_message(user_id, 'downloaded'))
            else:
                await processing_msg.edit_text(self.get_message(user_id, 'invalid_link'))
            
        except Exception as e:
            logger.error(f"Error downloading from URL: {e}")
            await processing_msg.edit_text(self.get_message(user_id, 'error', error=str(e)))
    
    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline queries"""
        query = update.inline_query.query
        user_id = update.inline_query.from_user.id
        
        if not query:
            return
        
        try:
            # Search for songs
            results = await self.song_recognizer.search_song(query)
            
            articles = []
            for result in results[:5]:  # Limit to 5 results
                articles.append(
                    telegram.InlineQueryResultArticle(
                        id=str(result['id']),
                        title=result['title'],
                        description=f"{result['artist']} - {result['album']}",
                        input_message_content=telegram.InputTextMessageContent(
                            message_text=f"🎵 {result['title']}\n👤 {result['artist']}\n💿 {result['album']}"
                        ),
                        thumb_url=result.get('image_url', ''),
                        reply_markup=telegram.InlineKeyboardMarkup([
                            [telegram.InlineKeyboardButton(
                                "🎵 Listen",
                                url=result.get('spotify_url', '')
                            )]
                        ])
                    )
                )
            
            await update.inline_query.answer(articles, cache_time=1)
            
        except Exception as e:
            logger.error(f"Error in inline query: {e}")
    
    def setup_handlers(self):
        """Setup all handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("statistics", self.statistics_command))
        self.application.add_handler(CommandHandler("language", self.language_command))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.AUDIO | filters.VOICE | filters.VIDEO | filters.VIDEO_NOTE, self.handle_audio_message))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        # Inline query handler
        self.application.add_handler(InlineQueryHandler(self.inline_query))
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            try:
                user_id = update.effective_user.id
                await update.effective_message.reply_text(
                    self.get_message(user_id, 'error', error=str(context.error))
                )
            except:
                pass
    
    def run(self):
        """Run the bot"""
        self.setup_handlers()
        
        # Add error handler
        self.application.add_error_handler(self.error_handler)
        
        # Create temp directory
        os.makedirs("temp", exist_ok=True)
        os.makedirs("downloads", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        logger.info("Starting bot...")
        self.application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    bot = MusicBot()
    bot.run()