"""
Helper functions for the bot
"""

import os
import re
import time
import subprocess
from datetime import datetime, timedelta
from typing import Optional, List

def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds <= 0:
        return "0:00"
    
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    
    Args:
        filename: Filename
        
    Returns:
        File extension (including dot)
    """
    return os.path.splitext(filename)[1].lower()

def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid
    
    Args:
        url: URL to check
        
    Returns:
        True if valid, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def clean_temp_files(file_path: Optional[str] = None):
    """
    Clean up temporary files
    
    Args:
        file_path: Specific file to delete, or None to clean all temp files
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return
        
        # Clean all files in temp directory
        temp_dir = "temp"
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    except Exception as e:
        print(f"Error cleaning temp files: {e}")

def is_admin(user_id: int) -> bool:
    """
    Check if user is admin
    
    Args:
        user_id: User ID to check
        
    Returns:
        True if admin, False otherwise
    """
    # Import here to avoid circular import
    from config import ADMIN_USER_ID
    return user_id == ADMIN_USER_ID

def get_bot_ping() -> int:
    """
    Get bot ping in milliseconds
    
    Returns:
        Ping time in milliseconds
    """
    try:
        start_time = time.time()
        # Simple ping test
        subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      timeout=5)
        end_time = time.time()
        return int((end_time - start_time) * 1000)
    except:
        return 0

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename or "unnamed"

def extract_youtube_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from URL
    
    Args:
        url: YouTube URL
        
    Returns:
        Video ID or None if not found
    """
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def extract_soundcloud_id(url: str) -> Optional[str]:
    """
    Extract SoundCloud track ID from URL
    
    Args:
        url: SoundCloud URL
        
    Returns:
        Track ID or None if not found
    """
    # SoundCloud URLs don't always have a clear ID pattern
    # This is a simplified extraction
    pattern = r'soundcloud\.com\/([^\/]+)\/([^\/]+)'
    match = re.search(pattern, url)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    
    return None

def is_audio_file(filename: str) -> bool:
    """
    Check if file is an audio file
    
    Args:
        filename: Filename to check
        
    Returns:
        True if audio file, False otherwise
    """
    audio_extensions = ['.mp3', '.m4a', '.wav', '.ogg', '.flac', '.aac', '.wma', '.opus']
    return get_file_extension(filename) in audio_extensions

def is_video_file(filename: str) -> bool:
    """
    Check if file is a video file
    
    Args:
        filename: Filename to check
        
    Returns:
        True if video file, False otherwise
    """
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
    return get_file_extension(filename) in video_extensions

def create_safe_filename(title: str, artist: str, extension: str = '.mp3') -> str:
    """
    Create safe filename from song title and artist
    
    Args:
        title: Song title
        artist: Artist name
        extension: File extension
        
    Returns:
        Safe filename
    """
    # Combine title and artist
    if title and artist:
        filename = f"{artist} - {title}{extension}"
    elif title:
        filename = f"{title}{extension}"
    else:
        filename = f"unknown_song{extension}"
    
    # Sanitize filename
    filename = sanitize_filename(filename)
    
    return filename

def get_platform_from_url(url: str) -> Optional[str]:
    """
    Get platform name from URL
    
    Args:
        url: URL to analyze
        
    Returns:
        Platform name or None if not recognized
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

def parse_duration_string(duration_str: str) -> int:
    """
    Parse duration string to seconds
    
    Args:
        duration_str: Duration string (e.g., "3:45", "1:23:45")
        
    Returns:
        Duration in seconds
    """
    try:
        parts = duration_str.split(':')
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        else:
            return 0
    except:
        return 0

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def is_weekend() -> bool:
    """
    Check if today is weekend
    
    Returns:
        True if weekend, False otherwise
    """
    today = datetime.now().weekday()
    return today >= 5  # 5=Saturday, 6=Sunday

def get_time_greeting() -> str:
    """
    Get time-based greeting
    
    Returns:
        Greeting string
    """
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 22:
        return "Good evening"
    else:
        return "Good night"

def format_number(number: int) -> str:
    """
    Format number with commas
    
    Args:
        number: Number to format
        
    Returns:
        Formatted number string
    """
    return "{:,}".format(number)

def calculate_percentage(part: int, total: int) -> float:
    """
    Calculate percentage
    
    Args:
        part: Part value
        total: Total value
        
    Returns:
        Percentage
    """
    if total == 0:
        return 0.0
    
    return (part / total) * 100

def get_file_hash(file_path: str) -> Optional[str]:
    """
    Get file hash for duplicate detection
    
    Args:
        file_path: Path to file
        
    Returns:
        File hash or None if error
    """
    try:
        import hashlib
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    except:
        return None

def is_port_in_use(port: int) -> bool:
    """
    Check if port is in use
    
    Args:
        port: Port number
        
    Returns:
        True if port is in use, False otherwise
    """
    try:
        import socket
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    except:
        return False

def get_system_info() -> dict:
    """
    Get system information
    
    Returns:
        Dictionary with system information
    """
    try:
        import platform
        import psutil
        
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'ram_total': psutil.virtual_memory().total,
            'ram_available': psutil.virtual_memory().available,
            'cpu_count': psutil.cpu_count(),
            'cpu_usage': psutil.cpu_percent(),
            'disk_usage': psutil.disk_usage('/').percent
        }
    except:
        return {
            'platform': 'Unknown',
            'platform_version': 'Unknown',
            'architecture': 'Unknown',
            'processor': 'Unknown',
            'ram_total': 0,
            'ram_available': 0,
            'cpu_count': 0,
            'cpu_usage': 0,
            'disk_usage': 0
        }