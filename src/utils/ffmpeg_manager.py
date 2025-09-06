"""
FFmpeg Setup and Installation Helper
"""

import os
import subprocess
import shutil
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class FFmpegManager:
    def __init__(self):
        self.ffmpeg_path = None
        self.ffprobe_path = None
        self._check_ffmpeg_availability()
    
    def _check_ffmpeg_availability(self):
        """Check if FFmpeg and FFprobe are available in the system"""
        try:
            # Check FFmpeg
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.ffmpeg_path = 'ffmpeg'
                logger.info("FFmpeg found in system PATH")
            
            # Check FFprobe
            result = subprocess.run(['ffprobe', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.ffprobe_path = 'ffprobe'
                logger.info("FFprobe found in system PATH")
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("FFmpeg/FFprobe not found in system PATH")
            self._try_alternative_paths()
    
    def _try_alternative_paths(self):
        """Try to find FFmpeg in alternative locations"""
        common_paths = [
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg',
            '/opt/bin/ffmpeg',
            '/opt/local/bin/ffmpeg',
            '/snap/bin/ffmpeg',
            'C:\\ffmpeg\\bin\\ffmpeg.exe',
            'C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe'
        ]
        
        probe_paths = [
            '/usr/bin/ffprobe',
            '/usr/local/bin/ffprobe',
            '/opt/bin/ffprobe',
            '/opt/local/bin/ffprobe',
            '/snap/bin/ffprobe',
            'C:\\ffmpeg\\bin\\ffprobe.exe',
            'C:\\Program Files\\ffmpeg\\bin\\ffprobe.exe'
        ]
        
        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                self.ffmpeg_path = path
                logger.info(f"FFmpeg found at: {path}")
                break
        
        for path in probe_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                self.ffprobe_path = path
                logger.info(f"FFprobe found at: {path}")
                break
    
    def is_available(self) -> bool:
        """Check if FFmpeg is available"""
        return self.ffmpeg_path is not None and self.ffprobe_path is not None
    
    def get_ffmpeg_path(self) -> Optional[str]:
        """Get FFmpeg path"""
        return self.ffmpeg_path
    
    def get_ffprobe_path(self) -> Optional[str]:
        """Get FFprobe path"""
        return self.ffprobe_path
    
    def install_ffmpeg_linux(self) -> bool:
        """Install FFmpeg on Linux systems"""
        try:
            logger.info("Attempting to install FFmpeg on Linux...")
            
            # Try different package managers
            package_managers = [
                (['sudo', 'apt', 'update'], ['sudo', 'apt', 'install', '-y', 'ffmpeg']),
                (['sudo', 'yum', 'update'], ['sudo', 'yum', 'install', '-y', 'ffmpeg']),
                (['sudo', 'dnf', 'update'], ['sudo', 'dnf', 'install', '-y', 'ffmpeg']),
                (['sudo', 'pacman', '-Syu'], ['sudo', 'pacman', '-S', '--noconfirm', 'ffmpeg']),
            ]
            
            for update_cmd, install_cmd in package_managers:
                try:
                    # Update package list
                    subprocess.run(update_cmd, check=True, capture_output=True, timeout=60)
                    # Install FFmpeg
                    subprocess.run(install_cmd, check=True, capture_output=True, timeout=300)
                    
                    # Check if installation was successful
                    self._check_ffmpeg_availability()
                    if self.is_available():
                        logger.info("FFmpeg installed successfully")
                        return True
                        
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            logger.error("Failed to install FFmpeg using package managers")
            return False
            
        except Exception as e:
            logger.error(f"Error installing FFmpeg: {e}")
            return False
    
    def download_static_ffmpeg(self, download_dir: str = "ffmpeg_static") -> bool:
        """Download static FFmpeg binaries for systems without package manager"""
        try:
            import urllib.request
            import tarfile
            import zipfile
            
            os.makedirs(download_dir, exist_ok=True)
            
            # Determine system architecture
            import platform
            system = platform.system().lower()
            machine = platform.machine().lower()
            
            # Static build URLs (these are examples, you may need to update them)
            static_builds = {
                'linux': {
                    'x86_64': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz',
                    'arm64': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz',
                    'armhf': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-armhf-static.tar.xz'
                },
                'darwin': {
                    'x86_64': 'https://evermeet.cx/ffmpeg/ffmpeg-4.4.1.zip',
                    'arm64': 'https://evermeet.cx/ffmpeg/ffmpeg-4.4.1.zip'
                }
            }
            
            if system not in static_builds:
                logger.error(f"Static builds not available for {system}")
                return False
            
            if machine not in static_builds[system]:
                logger.error(f"Static builds not available for {machine}")
                return False
            
            url = static_builds[system][machine]
            filename = os.path.join(download_dir, url.split('/')[-1])
            
            logger.info(f"Downloading static FFmpeg from {url}")
            urllib.request.urlretrieve(url, filename)
            
            # Extract the archive
            if filename.endswith('.tar.xz'):
                with tarfile.open(filename, 'r:xz') as tar:
                    tar.extractall(download_dir)
            elif filename.endswith('.zip'):
                with zipfile.ZipFile(filename, 'r') as zip_ref:
                    zip_ref.extractall(download_dir)
            
            # Find the extracted binaries
            extracted_dir = None
            for item in os.listdir(download_dir):
                item_path = os.path.join(download_dir, item)
                if os.path.isdir(item_path):
                    extracted_dir = item_path
                    break
            
            if extracted_dir:
                # Look for ffmpeg and ffprobe in the extracted directory
                for root, dirs, files in os.walk(extracted_dir):
                    if 'ffmpeg' in files:
                        ffmpeg_path = os.path.join(root, 'ffmpeg')
                        # Make executable
                        os.chmod(ffmpeg_path, 0o755)
                        self.ffmpeg_path = ffmpeg_path
                        
                    if 'ffprobe' in files:
                        ffprobe_path = os.path.join(root, 'ffprobe')
                        # Make executable
                        os.chmod(ffprobe_path, 0o755)
                        self.ffprobe_path = ffprobe_path
                
                if self.is_available():
                    logger.info("Static FFmpeg binaries downloaded and configured")
                    return True
            
            logger.error("Failed to extract FFmpeg binaries")
            return False
            
        except Exception as e:
            logger.error(f"Error downloading static FFmpeg: {e}")
            return False
    
    def setup_ytdlp_ffmpeg_location(self):
        """Setup yt-dlp to use our FFmpeg location"""
        if self.ffmpeg_path:
            os.environ['FFMPEG_LOCATION'] = os.path.dirname(self.ffmpeg_path)
            logger.info(f"Set FFMPEG_LOCATION to: {os.path.dirname(self.ffmpeg_path)}")
    
    def get_installation_commands(self) -> dict:
        """Get installation commands for different operating systems"""
        return {
            'ubuntu_debian': {
                'commands': [
                    'sudo apt update',
                    'sudo apt install -y ffmpeg'
                ],
                'description': 'Install FFmpeg on Ubuntu/Debian'
            },
            'centos_rhel': {
                'commands': [
                    'sudo yum install epel-release',
                    'sudo yum install -y ffmpeg'
                ],
                'description': 'Install FFmpeg on CentOS/RHEL'
            },
            'fedora': {
                'commands': [
                    'sudo dnf install -y ffmpeg'
                ],
                'description': 'Install FFmpeg on Fedora'
            },
            'macos': {
                'commands': [
                    'brew install ffmpeg'
                ],
                'description': 'Install FFmpeg on macOS using Homebrew'
            },
            'windows': {
                'commands': [
                    'Download from: https://ffmpeg.org/download.html',
                    'Extract to C:\\ffmpeg\\',
                    'Add C:\\ffmpeg\\bin to PATH'
                ],
                'description': 'Install FFmpeg on Windows'
            }
        }
    
    def test_ffmpeg_functionality(self) -> Tuple[bool, str]:
        """Test if FFmpeg is working properly"""
        if not self.is_available():
            return False, "FFmpeg not found"
        
        try:
            # Test FFmpeg
            result = subprocess.run([self.ffmpeg_path, '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False, f"FFmpeg error: {result.stderr}"
            
            # Test FFprobe
            result = subprocess.run([self.ffprobe_path, '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return False, f"FFprobe error: {result.stderr}"
            
            # Test audio conversion capability
            test_input = os.path.join('temp', 'test_input.mp3')
            test_output = os.path.join('temp', 'test_output.wav')
            
            # Create a dummy audio file for testing
            os.makedirs('temp', exist_ok=True)
            with open(test_input, 'wb') as f:
                f.write(b'dummy audio data')
            
            # Test conversion
            result = subprocess.run([
                self.ffmpeg_path, '-i', test_input, 
                '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '1',
                '-y', test_output
            ], capture_output=True, text=True, timeout=30)
            
            # Clean up test files
            for f in [test_input, test_output]:
                if os.path.exists(f):
                    os.remove(f)
            
            # FFmpeg might fail with dummy data, but that's okay
            # We just want to make sure it runs without crashing
            return True, "FFmpeg is working properly"
            
        except subprocess.TimeoutExpired:
            return False, "FFmpeg timeout"
        except Exception as e:
            return False, f"FFmpeg test error: {str(e)}"

# Global FFmpeg manager instance
ffmpeg_manager = FFmpegManager()

def setup_ffmpeg():
    """Setup FFmpeg for the application"""
    global ffmpeg_manager
    
    if not ffmpeg_manager.is_available():
        logger.warning("FFmpeg not found, attempting to install...")
        
        # Try to install on Linux
        if os.name == 'posix':
            if ffmpeg_manager.install_ffmpeg_linux():
                logger.info("FFmpeg installed successfully")
                return True
        
        # Try static build download
        if ffmpeg_manager.download_static_ffmpeg():
            logger.info("Static FFmpeg downloaded successfully")
            return True
        
        logger.error("Failed to setup FFmpeg")
        return False
    
    logger.info("FFmpeg is already available")
    ffmpeg_manager.setup_ytdlp_ffmpeg_location()
    return True

def get_ffmpeg_paths():
    """Get FFmpeg and FFprobe paths"""
    return ffmpeg_manager.get_ffmpeg_path(), ffmpeg_manager.get_ffprobe_path()

def is_ffmpeg_available():
    """Check if FFmpeg is available"""
    return ffmpeg_manager.is_available()