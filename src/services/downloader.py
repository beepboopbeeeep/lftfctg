"""
Download Service for various platforms
"""

import asyncio
import logging
import os
import re
import subprocess
from typing import Optional, Dict, List
from urllib.parse import urlparse

import yt_dlp
import requests
import instaloader

from utils.ffmpeg_manager import ffmpeg_manager, setup_ffmpeg, is_ffmpeg_available

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self):
        # Setup FFmpeg first
        self.ffmpeg_available = setup_ffmpeg()
        
        # Configure yt-dlp options based on FFmpeg availability
        if self.ffmpeg_available:
            self.ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': False,
                'no_warnings': False,
                'extract_flat': 'discard_in_playlist',
                'fragment_retries': 10,
                'retry_sleep_functions': {
                    'http': lambda n: min(n * 2, 10),
                    'fragment': lambda n: min(n * 2, 10),
                },
            }
        else:
            # Fallback options without FFmpeg post-processing
            self.ydl_opts = {
                'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'quiet': False,
                'no_warnings': False,
                'extract_flat': 'discard_in_playlist',
                'fragment_retries': 10,
                'retry_sleep_functions': {
                    'http': lambda n: min(n * 2, 10),
                    'fragment': lambda n: min(n * 2, 10),
                },
                'postprocessors': [],  # No FFmpeg post-processors
            }
        
        self.instaloader_instance = instaloader.Instaloader()
        
        # Create downloads directory
        os.makedirs("downloads", exist_ok=True)
        
        if not self.ffmpeg_available:
            logger.warning("FFmpeg not available. Some features may be limited.")
    
    async def download_song(self, query: str) -> Optional[str]:
        """
        Download song by searching for it
        
        Args:
            query: Song search query
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            if not self.ffmpeg_available:
                logger.warning("FFmpeg not available. Download quality may be limited.")
            
            # Search YouTube for the song
            search_opts = self.ydl_opts.copy()
            search_opts.update({
                'quiet': True,
                'default_search': 'auto',
                'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
            })
            
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
                downloaded_file = ydl.prepare_filename(info)
                
                # Check if file exists and return the path
                if os.path.exists(downloaded_file):
                    logger.info(f"Song downloaded successfully: {downloaded_file}")
                    return downloaded_file
                else:
                    # Try to find the downloaded file
                    base_name = os.path.splitext(downloaded_file)[0]
                    for ext in ['.mp3', '.m4a', '.webm', '.opus']:
                        test_file = f"{base_name}{ext}"
                        if os.path.exists(test_file):
                            logger.info(f"Song downloaded successfully: {test_file}")
                            return test_file
            
            logger.warning(f"Could not find downloaded file for query: {query}")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading song: {e}")
            return None
    
    async def download_from_url(self, url: str) -> Optional[str]:
        """
        Download content from URL based on platform
        
        Args:
            url: URL to download from
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Determine platform
            platform = self._get_platform_from_url(url)
            
            if platform == 'youtube':
                return await self._download_from_youtube(url)
            elif platform == 'instagram':
                return await self._download_from_instagram(url)
            elif platform == 'tiktok':
                return await self._download_from_tiktok(url)
            elif platform == 'pinterest':
                return await self._download_from_pinterest(url)
            elif platform == 'soundcloud':
                return await self._download_from_soundcloud(url)
            else:
                logger.error(f"Unsupported platform: {platform}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading from URL {url}: {e}")
            return None
    
    def _get_platform_from_url(self, url: str) -> Optional[str]:
        """
        Determine platform from URL
        
        Args:
            url: URL to analyze
            
        Returns:
            Platform name or None if not supported
        """
        url_lower = url.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'instagram.com' in url_lower or 'instagr.am' in url_lower:
            return 'instagram'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'pinterest.com' in url_lower or 'pin.it' in url_lower:
            return 'pinterest'
        elif 'soundcloud.com' in url_lower:
            return 'soundcloud'
        else:
            return None
    
    async def _download_from_youtube(self, url: str) -> Optional[str]:
        """
        Download from YouTube
        
        Args:
            url: YouTube URL
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                # Convert to MP3 if needed
                if downloaded_file.endswith(('.webm', '.m4a')):
                    mp3_file = os.path.splitext(downloaded_file)[0] + '.mp3'
                    if os.path.exists(mp3_file):
                        logger.info(f"YouTube content downloaded successfully: {mp3_file}")
                        return mp3_file
                
                if os.path.exists(downloaded_file):
                    logger.info(f"YouTube content downloaded successfully: {downloaded_file}")
                    return downloaded_file
            
            return None
            
        except Exception as e:
            logger.error(f"Error downloading from YouTube: {e}")
            return None
    
    async def _download_from_instagram(self, url: str) -> Optional[str]:
        """
        Download from Instagram
        
        Args:
            url: Instagram URL
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Extract shortcode from URL
            shortcode = self._extract_instagram_shortcode(url)
            if not shortcode:
                return None
            
            # Download using instaloader
            post = instaloader.Post.from_shortcode(self.instaloader_instance.context, shortcode)
            
            if post.is_video:
                # Download video
                video_url = post.video_url
                filename = f"downloads/instagram_{shortcode}.mp4"
                
                # Download video file
                response = requests.get(video_url, stream=True)
                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    logger.info(f"Instagram video downloaded successfully: {filename}")
                    return filename
            else:
                # Download image
                image_url = post.url
                filename = f"downloads/instagram_{shortcode}.jpg"
                
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    logger.info(f"Instagram image downloaded successfully: {filename}")
                    return filename
            
            return None
            
        except Exception as e:
            logger.error(f"Error downloading from Instagram: {e}")
            return None
    
    async def _download_from_tiktok(self, url: str) -> Optional[str]:
        """
        Download from TikTok
        
        Args:
            url: TikTok URL
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Use yt-dlp for TikTok (it supports TikTok)
            tiktok_opts = {
                'format': 'best',
                'outtmpl': 'downloads/tiktok_%(id)s.%(ext)s',
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(tiktok_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                if os.path.exists(downloaded_file):
                    logger.info(f"TikTok content downloaded successfully: {downloaded_file}")
                    return downloaded_file
            
            return None
            
        except Exception as e:
            logger.error(f"Error downloading from TikTok: {e}")
            return None
    
    async def _download_from_pinterest(self, url: str) -> Optional[str]:
        """
        Download from Pinterest
        
        Args:
            url: Pinterest URL
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Use yt-dlp for Pinterest
            pinterest_opts = {
                'format': 'best',
                'outtmpl': 'downloads/pinterest_%(id)s.%(ext)s',
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(pinterest_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                if os.path.exists(downloaded_file):
                    logger.info(f"Pinterest content downloaded successfully: {downloaded_file}")
                    return downloaded_file
            
            return None
            
        except Exception as e:
            logger.error(f"Error downloading from Pinterest: {e}")
            return None
    
    async def _download_from_soundcloud(self, url: str) -> Optional[str]:
        """
        Download from SoundCloud
        
        Args:
            url: SoundCloud URL
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Use yt-dlp for SoundCloud
            soundcloud_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'downloads/soundcloud_%(title)s.%(ext)s',
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(soundcloud_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                # Convert to MP3 if needed
                if downloaded_file.endswith(('.webm', '.m4a')):
                    mp3_file = os.path.splitext(downloaded_file)[0] + '.mp3'
                    if os.path.exists(mp3_file):
                        logger.info(f"SoundCloud content downloaded successfully: {mp3_file}")
                        return mp3_file
                
                if os.path.exists(downloaded_file):
                    logger.info(f"SoundCloud content downloaded successfully: {downloaded_file}")
                    return downloaded_file
            
            return None
            
        except Exception as e:
            logger.error(f"Error downloading from SoundCloud: {e}")
            return None
    
    def _extract_instagram_shortcode(self, url: str) -> Optional[str]:
        """
        Extract Instagram shortcode from URL
        
        Args:
            url: Instagram URL
            
        Returns:
            Shortcode or None if not found
        """
        patterns = [
            r'instagram\.com/p/([^/]+)',
            r'instagram\.com/reel/([^/]+)',
            r'instagr\.am/p/([^/]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                shortcode = match.group(1)
                # Remove any trailing slashes or parameters
                shortcode = shortcode.split('/')[0].split('?')[0]
                return shortcode
        
        return None
    
    async def extract_audio_from_video(self, video_path: str) -> Optional[str]:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            Path to extracted audio file or None if failed
        """
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return None
            
            if not self.ffmpeg_available:
                logger.error("FFmpeg not available. Cannot extract audio from video.")
                return None
            
            # Generate output path
            base_name = os.path.splitext(video_path)[0]
            audio_path = f"{base_name}.mp3"
            
            # Get FFmpeg path
            ffmpeg_path, ffprobe_path = ffmpeg_manager.get_ffmpeg_path(), ffmpeg_manager.get_ffprobe_path()
            
            if not ffmpeg_path:
                logger.error("FFmpeg not found. Cannot extract audio.")
                return None
            
            # Use ffmpeg to extract audio
            cmd = [
                ffmpeg_path,
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'libmp3lame',
                '-ab', '192k',
                '-ar', '44100',
                '-y',  # Overwrite output file
                audio_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0 and os.path.exists(audio_path):
                logger.info(f"Audio extracted successfully: {audio_path}")
                return audio_path
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Error extracting audio: {error_msg}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting audio from video: {e}")
            return None
    
    async def get_download_info(self, url: str) -> Optional[Dict]:
        """
        Get information about downloadable content without downloading
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary with content information or None if failed
        """
        try:
            platform = self._get_platform_from_url(url)
            
            if platform == 'youtube':
                return await self._get_youtube_info(url)
            elif platform == 'soundcloud':
                return await self._get_soundcloud_info(url)
            else:
                # For other platforms, we might not be able to get info without downloading
                return None
                
        except Exception as e:
            logger.error(f"Error getting download info: {e}")
            return None
    
    def get_ffmpeg_status(self) -> Dict:
        """
        Get FFmpeg status information
        
        Returns:
            Dictionary with FFmpeg status
        """
        return {
            'available': self.ffmpeg_available,
            'ffmpeg_path': ffmpeg_manager.get_ffmpeg_path(),
            'ffprobe_path': ffmpeg_manager.get_ffprobe_path(),
            'installation_commands': ffmpeg_manager.get_installation_commands()
        }
    
    async def _get_youtube_info(self, url: str) -> Optional[Dict]:
        """
        Get YouTube video information
        
        Args:
            url: YouTube URL
            
        Returns:
            Dictionary with video information
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'platform': 'youtube'
                }
                
        except Exception as e:
            logger.error(f"Error getting YouTube info: {e}")
            return None
    
    async def _get_soundcloud_info(self, url: str) -> Optional[Dict]:
        """
        Get SoundCloud track information
        
        Args:
            url: SoundCloud URL
            
        Returns:
            Dictionary with track information
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'platform': 'soundcloud'
                }
                
        except Exception as e:
            logger.error(f"Error getting SoundCloud info: {e}")
            return None