"""
Song Model
"""

from datetime import datetime
from typing import Optional

class Song:
    def __init__(
        self,
        id: int = 0,
        title: str = "Unknown",
        artist: str = "Unknown",
        album: str = "Unknown",
        duration: int = 0,
        genre: str = "",
        year: int = 0,
        spotify_url: str = "",
        apple_url: str = "",
        youtube_url: str = "",
        image_url: str = "",
        shazam_id: str = "",
        isrc: str = "",
        recognized_at: Optional[datetime] = None,
        user_id: Optional[int] = None
    ):
        self.id = id
        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration
        self.genre = genre
        self.year = year
        self.spotify_url = spotify_url
        self.apple_url = apple_url
        self.youtube_url = youtube_url
        self.image_url = image_url
        self.shazam_id = shazam_id
        self.isrc = isrc
        self.recognized_at = recognized_at or datetime.now()
        self.user_id = user_id
    
    def to_dict(self) -> dict:
        """Convert song to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'duration': self.duration,
            'genre': self.genre,
            'year': self.year,
            'spotify_url': self.spotify_url,
            'apple_url': self.apple_url,
            'youtube_url': self.youtube_url,
            'image_url': self.image_url,
            'shazam_id': self.shazam_id,
            'isrc': self.isrc,
            'recognized_at': self.recognized_at.isoformat() if self.recognized_at else None,
            'user_id': self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Song':
        """Create song from dictionary"""
        return cls(
            id=data.get('id', 0),
            title=data.get('title', 'Unknown'),
            artist=data.get('artist', 'Unknown'),
            album=data.get('album', 'Unknown'),
            duration=data.get('duration', 0),
            genre=data.get('genre', ''),
            year=data.get('year', 0),
            spotify_url=data.get('spotify_url', ''),
            apple_url=data.get('apple_url', ''),
            youtube_url=data.get('youtube_url', ''),
            image_url=data.get('image_url', ''),
            shazam_id=data.get('shazam_id', ''),
            isrc=data.get('isrc', ''),
            recognized_at=datetime.fromisoformat(data['recognized_at']) if data.get('recognized_at') else None,
            user_id=data.get('user_id')
        )
    
    def __str__(self) -> str:
        return f"Song(title={self.title}, artist={self.artist}, album={self.album})"
    
    def __repr__(self) -> str:
        return self.__str__()