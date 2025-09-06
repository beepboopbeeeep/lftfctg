"""
Firebase Service for data storage and retrieval
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

from models.user import User
from models.song import Song

logger = logging.getLogger(__name__)

class FirebaseService:
    def __init__(self):
        self.db = None
        self.initialized = False
        
        if FIREBASE_AVAILABLE:
            self._initialize_firebase()
        else:
            logger.warning("Firebase not available, using local storage")
            self._use_local_storage()
    
    def _initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Try to load credentials from file
                cred_path = "config/firebase-credentials.json"
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    # Use default credentials (for local development)
                    firebase_admin.initialize_app()
            
            self.db = firestore.client()
            self.initialized = True
            logger.info("Firebase initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            self._use_local_storage()
    
    def _use_local_storage(self):
        """Use local storage instead of Firebase"""
        self.local_storage = {
            'users': {},
            'songs': {},
            'statistics': {
                'total_users': 0,
                'songs_recognized': 0,
                'songs_downloaded': 0,
                'last_updated': datetime.now().isoformat()
            }
        }
        logger.info("Using local storage")
    
    async def save_user(self, user: User) -> bool:
        """
        Save user information
        
        Args:
            user: User object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user_data = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'language': user.language,
                'joined_at': user.joined_at.isoformat() if user.joined_at else datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'is_active': True
            }
            
            if self.initialized and self.db:
                # Save to Firebase
                self.db.collection('users').document(str(user.id)).set(user_data)
            else:
                # Save to local storage
                self.local_storage['users'][str(user.id)] = user_data
                self.local_storage['statistics']['total_users'] = len(self.local_storage['users'])
            
            logger.info(f"User saved: {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """
        Get user information
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        try:
            if self.initialized and self.db:
                # Get from Firebase
                doc = self.db.collection('users').document(str(user_id)).get()
                if doc.exists:
                    data = doc.to_dict()
                    return User(
                        id=data.get('id', user_id),
                        username=data.get('username'),
                        first_name=data.get('first_name'),
                        last_name=data.get('last_name'),
                        language=data.get('language', 'en'),
                        joined_at=datetime.fromisoformat(data.get('joined_at', datetime.now().isoformat()))
                    )
            else:
                # Get from local storage
                user_data = self.local_storage['users'].get(str(user_id))
                if user_data:
                    return User(
                        id=user_data.get('id', user_id),
                        username=user_data.get('username'),
                        first_name=user_data.get('first_name'),
                        last_name=user_data.get('last_name'),
                        language=user_data.get('language', 'en'),
                        joined_at=datetime.fromisoformat(user_data.get('joined_at', datetime.now().isoformat()))
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    async def update_user_language(self, user_id: int, language: str) -> bool:
        """
        Update user language preference
        
        Args:
            user_id: User ID
            language: Language code ('en' or 'fa')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.initialized and self.db:
                # Update in Firebase
                self.db.collection('users').document(str(user_id)).update({
                    'language': language,
                    'last_activity': datetime.now().isoformat()
                })
            else:
                # Update in local storage
                if str(user_id) in self.local_storage['users']:
                    self.local_storage['users'][str(user_id)]['language'] = language
                    self.local_storage['users'][str(user_id)]['last_activity'] = datetime.now().isoformat()
            
            logger.info(f"User language updated: {user_id} -> {language}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user language: {e}")
            return False
    
    async def get_all_users(self) -> List[User]:
        """
        Get all users
        
        Returns:
            List of User objects
        """
        try:
            users = []
            
            if self.initialized and self.db:
                # Get from Firebase
                users_ref = self.db.collection('users')
                docs = users_ref.stream()
                
                for doc in docs:
                    data = doc.to_dict()
                    users.append(User(
                        id=data.get('id', int(doc.id)),
                        username=data.get('username'),
                        first_name=data.get('first_name'),
                        last_name=data.get('last_name'),
                        language=data.get('language', 'en'),
                        joined_at=datetime.fromisoformat(data.get('joined_at', datetime.now().isoformat()))
                    ))
            else:
                # Get from local storage
                for user_id, user_data in self.local_storage['users'].items():
                    users.append(User(
                        id=user_data.get('id', int(user_id)),
                        username=user_data.get('username'),
                        first_name=user_data.get('first_name'),
                        last_name=user_data.get('last_name'),
                        language=user_data.get('language', 'en'),
                        joined_at=datetime.fromisoformat(user_data.get('joined_at', datetime.now().isoformat()))
                    ))
            
            logger.info(f"Retrieved {len(users)} users")
            return users
            
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def save_song(self, song: Song) -> bool:
        """
        Save song information
        
        Args:
            song: Song object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            song_data = {
                'title': song.title,
                'artist': song.artist,
                'album': song.album,
                'duration': song.duration,
                'genre': song.genre,
                'year': song.year,
                'spotify_url': song.spotify_url,
                'apple_url': song.apple_url,
                'youtube_url': song.youtube_url,
                'image_url': song.image_url,
                'shazam_id': song.shazam_id,
                'isrc': song.isrc,
                'recognized_at': song.recognized_at.isoformat() if song.recognized_at else datetime.now().isoformat(),
                'user_id': song.user_id
            }
            
            if self.initialized and self.db:
                # Save to Firebase
                self.db.collection('songs').document(song.shazam_id or str(song.id)).set(song_data)
            else:
                # Save to local storage
                song_id = song.shazam_id or str(song.id)
                self.local_storage['songs'][song_id] = song_data
            
            logger.info(f"Song saved: {song.title} - {song.artist}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving song: {e}")
            return False
    
    async def get_song(self, song_id: str) -> Optional[Song]:
        """
        Get song information
        
        Args:
            song_id: Song ID (Shazam ID or custom ID)
            
        Returns:
            Song object or None if not found
        """
        try:
            if self.initialized and self.db:
                # Get from Firebase
                doc = self.db.collection('songs').document(song_id).get()
                if doc.exists:
                    data = doc.to_dict()
                    return Song(
                        id=data.get('id', 0),
                        title=data.get('title'),
                        artist=data.get('artist'),
                        album=data.get('album'),
                        duration=data.get('duration', 0),
                        genre=data.get('genre'),
                        year=data.get('year', 0),
                        spotify_url=data.get('spotify_url'),
                        apple_url=data.get('apple_url'),
                        youtube_url=data.get('youtube_url'),
                        image_url=data.get('image_url'),
                        shazam_id=data.get('shazam_id'),
                        isrc=data.get('isrc'),
                        recognized_at=datetime.fromisoformat(data.get('recognized_at', datetime.now().isoformat())),
                        user_id=data.get('user_id')
                    )
            else:
                # Get from local storage
                song_data = self.local_storage['songs'].get(song_id)
                if song_data:
                    return Song(
                        id=song_data.get('id', 0),
                        title=song_data.get('title'),
                        artist=song_data.get('artist'),
                        album=song_data.get('album'),
                        duration=song_data.get('duration', 0),
                        genre=song_data.get('genre'),
                        year=song_data.get('year', 0),
                        spotify_url=song_data.get('spotify_url'),
                        apple_url=song_data.get('apple_url'),
                        youtube_url=song_data.get('youtube_url'),
                        image_url=song_data.get('image_url'),
                        shazam_id=song_data.get('shazam_id'),
                        isrc=song_data.get('isrc'),
                        recognized_at=datetime.fromisoformat(song_data.get('recognized_at', datetime.now().isoformat())),
                        user_id=song_data.get('user_id')
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting song: {e}")
            return None
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get bot statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            if self.initialized and self.db:
                # Get from Firebase
                stats_doc = self.db.collection('statistics').document('bot_stats').get()
                if stats_doc.exists:
                    return stats_doc.to_dict()
                else:
                    # Calculate statistics
                    users_count = len(list(self.db.collection('users').stream()))
                    songs_count = len(list(self.db.collection('songs').stream()))
                    
                    stats = {
                        'total_users': users_count,
                        'songs_recognized': songs_count,
                        'songs_downloaded': songs_count,  # Assuming all recognized songs are downloaded
                        'last_updated': datetime.now().isoformat()
                    }
                    
                    # Save statistics
                    self.db.collection('statistics').document('bot_stats').set(stats)
                    return stats
            else:
                # Get from local storage
                return self.local_storage['statistics']
                
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                'total_users': 0,
                'songs_recognized': 0,
                'songs_downloaded': 0,
                'last_updated': datetime.now().isoformat()
            }
    
    async def increment_stat(self, stat_name: str) -> bool:
        """
        Increment a statistic
        
        Args:
            stat_name: Name of the statistic to increment
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.initialized and self.db:
                # Get current statistics
                stats_doc = self.db.collection('statistics').document('bot_stats')
                doc = stats_doc.get()
                
                if doc.exists:
                    current_stats = doc.to_dict()
                else:
                    current_stats = {
                        'total_users': 0,
                        'songs_recognized': 0,
                        'songs_downloaded': 0,
                        'last_updated': datetime.now().isoformat()
                    }
                
                # Increment the specified statistic
                if stat_name in current_stats:
                    current_stats[stat_name] += 1
                else:
                    current_stats[stat_name] = 1
                
                current_stats['last_updated'] = datetime.now().isoformat()
                
                # Save updated statistics
                stats_doc.set(current_stats)
            else:
                # Update local storage
                if stat_name in self.local_storage['statistics']:
                    self.local_storage['statistics'][stat_name] += 1
                else:
                    self.local_storage['statistics'][stat_name] = 1
                
                self.local_storage['statistics']['last_updated'] = datetime.now().isoformat()
            
            logger.info(f"Statistic incremented: {stat_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing statistic: {e}")
            return False
    
    async def save_broadcast_message(self, message: str, duration_hours: int, sent_by: int) -> str:
        """
        Save broadcast message information
        
        Args:
            message: Message content
            duration_hours: Duration in hours (0 for permanent)
            sent_by: User ID who sent the broadcast
            
        Returns:
            Message ID
        """
        try:
            message_id = f"broadcast_{datetime.now().timestamp()}"
            
            broadcast_data = {
                'id': message_id,
                'message': message,
                'duration_hours': duration_hours,
                'sent_by': sent_by,
                'sent_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=duration_hours)).isoformat() if duration_hours > 0 else None,
                'is_active': True
            }
            
            if self.initialized and self.db:
                # Save to Firebase
                self.db.collection('broadcasts').document(message_id).set(broadcast_data)
            else:
                # Save to local storage
                if 'broadcasts' not in self.local_storage:
                    self.local_storage['broadcasts'] = {}
                self.local_storage['broadcasts'][message_id] = broadcast_data
            
            logger.info(f"Broadcast message saved: {message_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"Error saving broadcast message: {e}")
            return ""
    
    async def get_active_broadcasts(self) -> List[Dict]:
        """
        Get active broadcast messages
        
        Returns:
            List of active broadcast messages
        """
        try:
            broadcasts = []
            current_time = datetime.now()
            
            if self.initialized and self.db:
                # Get from Firebase
                broadcasts_ref = self.db.collection('broadcasts')
                docs = broadcasts_ref.stream()
                
                for doc in docs:
                    data = doc.to_dict()
                    if data.get('is_active', False):
                        # Check if expired
                        expires_at = data.get('expires_at')
                        if expires_at:
                            expires_time = datetime.fromisoformat(expires_at)
                            if current_time > expires_time:
                                # Mark as inactive
                                doc.reference.update({'is_active': False})
                                continue
                        
                        broadcasts.append(data)
            else:
                # Get from local storage
                if 'broadcasts' in self.local_storage:
                    for broadcast_id, broadcast_data in self.local_storage['broadcasts'].items():
                        if broadcast_data.get('is_active', False):
                            # Check if expired
                            expires_at = broadcast_data.get('expires_at')
                            if expires_at:
                                expires_time = datetime.fromisoformat(expires_at)
                                if current_time > expires_time:
                                    # Mark as inactive
                                    broadcast_data['is_active'] = False
                                    continue
                            
                            broadcasts.append(broadcast_data)
            
            logger.info(f"Retrieved {len(broadcasts)} active broadcasts")
            return broadcasts
            
        except Exception as e:
            logger.error(f"Error getting active broadcasts: {e}")
            return []
    
    async def cleanup_expired_data(self):
        """Clean up expired data"""
        try:
            current_time = datetime.now()
            
            if self.initialized and self.db:
                # Clean up expired broadcasts
                broadcasts_ref = self.db.collection('broadcasts')
                docs = broadcasts_ref.stream()
                
                for doc in docs:
                    data = doc.to_dict()
                    expires_at = data.get('expires_at')
                    if expires_at:
                        expires_time = datetime.fromisoformat(expires_at)
                        if current_time > expires_time:
                            doc.reference.delete()
            else:
                # Clean up local storage
                if 'broadcasts' in self.local_storage:
                    expired_broadcasts = []
                    for broadcast_id, broadcast_data in self.local_storage['broadcasts'].items():
                        expires_at = broadcast_data.get('expires_at')
                        if expires_at:
                            expires_time = datetime.fromisoformat(expires_at)
                            if current_time > expires_time:
                                expired_broadcasts.append(broadcast_id)
                    
                    for broadcast_id in expired_broadcasts:
                        del self.local_storage['broadcasts'][broadcast_id]
            
            logger.info("Expired data cleanup completed")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired data: {e}")