"""
Telegram Music Bot - Main Configuration
All variables are defined in code (no .env file)
"""

# Bot Configuration
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
ADMIN_USER_ID = 123456789  # Replace with your admin user ID

# Firebase Configuration (Optional - for cloud deployment)
FIREBASE_CREDENTIALS_PATH = "config/firebase-credentials.json"
FIREBASE_DATABASE_URL = "https://your-project.firebaseio.com"

# Music Recognition Configuration
SHAZAM_MAX_RETRIES = 3
SHAZAM_TIMEOUT = 30

# Download Configuration
DOWNLOAD_TIMEOUT = 300
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
TEMP_FILES_CLEANUP = True

# Supported Audio Formats
AUDIO_FORMATS = ['.mp3', '.m4a', '.wav', '.ogg', '.flac', '.aac']
VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']

# Social Media Platforms
SOCIAL_MEDIA_PLATFORMS = {
    'youtube': ['youtube.com', 'youtu.be'],
    'instagram': ['instagram.com', 'instagr.am'],
    'tiktok': ['tiktok.com'],
    'pinterest': ['pinterest.com', 'pin.it'],
    'soundcloud': ['soundcloud.com']
}

# Bot Messages (Multi-language support)
BOT_MESSAGES = {
    'en': {
        'welcome': "🎵 Welcome to Music Recognition Bot!\n\nI can recognize songs from audio/video files and download them for you.\n\nFeatures:\n• Song recognition from audio/video\n• Download from YouTube, Instagram, TikTok, Pinterest, SoundCloud\n• Edit song information\n• Inline search in groups/channels\n• Multi-language support\n\nChoose your language:",
        'language_selected': "✅ Language set to English",
        'main_menu': "🎵 Main Menu\n\nWhat would you like to do?",
        'send_audio': "🎵 Send me an audio or video file to recognize the song",
        'send_link': "🔗 Send me a link from YouTube, Instagram, TikTok, Pinterest, or SoundCloud",
        'processing': "⏳ Processing...",
        'recognizing': "🎵 Recognizing song...",
        'song_found': "🎉 Song Found!\n\n🎵 Title: {title}\n👤 Artist: {artist}\n💿 Album: {album}\n⏱️ Duration: {duration}",
        'song_not_found': "❌ Sorry, couldn't recognize the song",
        'downloading': "⏳ Downloading song...",
        'downloaded': "✅ Song downloaded successfully!",
        'error': "❌ An error occurred: {error}",
        'back': "🔙 Back",
        'statistics': "📊 Bot Statistics\n\n👥 Total Users: {users}\n🎵 Songs Recognized: {recognized}\n⬇️ Songs Downloaded: {downloaded}\n🟢 Status: Online\n📡 Ping: {ping}ms",
        'edit_song': "✏️ Edit Song Information\n\nSend me the song file first",
        'edit_info': "✏️ Send me the new information in this format:\n\nTitle: [song title]\nArtist: [artist name]\nAlbum: [album name]",
        'info_updated': "✅ Song information updated!",
        'broadcast': "📢 Broadcast Message\n\nSend me the message to broadcast to all users",
        'broadcast_sent': "✅ Message sent to {count} users",
        'broadcast_duration': "⏱️ Message will be deleted after {hours} hours",
        'invalid_link': "❌ Invalid link or unsupported platform",
        'file_too_large': "❌ File is too large (max 50MB)",
        'unsupported_format': "❌ Unsupported file format",
        'admin_only': "❌ This command is for admins only"
    },
    'fa': {
        'welcome': "🎵 به ربات تشخیص موسیقی خوش آمدید!\n\nمن می‌توانم آهنگ‌ها را از فایل‌های صوتی/تصویری تشخیص دهم و برای شما دانلود کنم.\n\nقابلیت‌ها:\n• تشخیص آهنگ از فایل صوتی/تصویری\n• دانلود از یوتیوب، اینستاگرام، تیک‌تاک، پینترست، ساندکلاد\n• ویرایش اطلاعات آهنگ\n• جستجوی اینلاین در گروه‌ها/کانال‌ها\n• پشتیبانی از چند زبان\n\nزبان خود را انتخاب کنید:",
        'language_selected': "✅ زبان به فارسی تنظیم شد",
        'main_menu': "🎵 منوی اصلی\n\nچه کاری می‌خواهید انجام دهید؟",
        'send_audio': "🎵 برای تشخیص آهنگ، یک فایل صوتی یا تصویری برایم ارسال کنید",
        'send_link': "🔗 لینکی از یوتیوب، اینستاگرام، تیک‌تاک، پینترست یا ساندکلاد برایم ارسال کنید",
        'processing': "⏳ در حال پردازش...",
        'recognizing': "🎵 در حال تشخیص آهنگ...",
        'song_found': "🎉 آهنگ پیدا شد!\n\n🎵 عنوان: {title}\n👤 هنرمند: {artist}\n💿 آلبوم: {album}\n⏱️ مدت: {duration}",
        'song_not_found': "❌ متأسفانه نتوانستم آهنگ را تشخیص دهم",
        'downloading': "⏳ در حال دانلود آهنگ...",
        'downloaded': "✅ آهنگ با موفقیت دانلود شد!",
        'error': "❌ خطایی رخ داد: {error}",
        'back': "🔙 بازگشت",
        'statistics': "📊 آمار ربات\n\n👥 کل کاربران: {users}\n🎵 آهنگ‌های تشخیص داده شده: {recognized}\n⬇️ آهنگ‌های دانلود شده: {downloaded}\n🟢 وضعیت: آنلاین\n📡 پینگ: {ping}ms",
        'edit_song': "✏️ ویرایش اطلاعات آهنگ\n\nابتدا فایل آهنگ را برایم ارسال کنید",
        'edit_info': "✏️ اطلاعات جدید را در این قالب برایم ارسال کنید:\n\nعنوان: [عنوان آهنگ]\nهنرمند: [نام هنرمند]\nآلبوم: [نام آلبوم]",
        'info_updated': "✅ اطلاعات آهنگ به‌روزرسانی شد!",
        'broadcast': "📢 ارسال پیام همگانی\n\nپیامی که می‌خواهید برای همه کاربران ارسال شود را برایم بفرستید",
        'broadcast_sent': "✅ پیام برای {count} کاربر ارسال شد",
        'broadcast_duration': "⏱️ پیام پس از {hours} ساعت حذف خواهد شد",
        'invalid_link': "❌ لینک نامعتبر یا پلتفرم پشتیبانی نشده",
        'file_too_large': "❌ فایل خیلی بزرگ است (حداکثر 50 مگابایت)",
        'unsupported_format': "❌ فرمت فایل پشتیبانی نمی‌شود",
        'admin_only': "❌ این دستور فقط برای ادمین‌ها است"
    }
}
