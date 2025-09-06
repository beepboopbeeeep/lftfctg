"""
User Model
"""

from datetime import datetime
from typing import Optional

class User:
    def __init__(
        self,
        id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language: str = 'en',
        joined_at: Optional[datetime] = None,
        is_active: bool = True
    ):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.language = language
        self.joined_at = joined_at or datetime.now()
        self.is_active = is_active
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'language': self.language,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create user from dictionary"""
        return cls(
            id=data.get('id', 0),
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            language=data.get('language', 'en'),
            joined_at=datetime.fromisoformat(data['joined_at']) if data.get('joined_at') else None,
            is_active=data.get('is_active', True)
        )
    
    def __str__(self) -> str:
        return f"User(id={self.id}, username={self.username}, first_name={self.first_name})"
    
    def __repr__(self) -> str:
        return self.__str__()