"""
Song Recognition Service using ShazamIO
"""

import asyncio
import logging
import os
from typing import Dict, Optional, List

from shazamio import Shazam, Serialize

logger = logging.getLogger(__name__)

class SongRecognizer:
    def __init__(self, shazam: Shazam):
        self.shazam = shazam
    
    async def recognize_song(self, file_path: str) -> Optional[Dict]:
        """
        Recognize song from audio file
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary with song information or None if not found
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            # Recognize song using ShazamIO
            result = await self.shazam.recognize(file_path)
            
            if result and result.get('track'):
                track = result['track']
                
                # Extract song information
                song_info = {
                    'title': track.get('title', 'Unknown'),
                    'artist': track.get('subtitle', 'Unknown'),
                    'album': track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', 'Unknown'),
                    'duration': track.get('duration', 0),
                    'genre': track.get('genres', {}).get('primary', ''),
                    'year': track.get('year', 0),
                    'spotify_url': track.get('hub', {}).get('actions', [{}])[0].get('uri', ''),
                    'apple_url': track.get('hub', {}).get('options', [{}])[0].get('actions', [{}])[0].get('uri', ''),
                    'youtube_url': track.get('hub', {}).get('options', [{}])[1].get('actions', [{}])[0].get('uri', ''),
                    'image_url': track.get('images', {}).get('coverarthq', ''),
                    'shazam_id': track.get('key', ''),
                    'isrc': track.get('isrc', '')
                }
                
                logger.info(f"Song recognized: {song_info['title']} - {song_info['artist']}")
                return song_info
            else:
                logger.info("No song found in the audio file")
                return None
                
        except Exception as e:
            logger.error(f"Error recognizing song: {e}")
            return None
    
    async def search_song(self, query: str) -> List[Dict]:
        """
        Search for songs by query
        
        Args:
            query: Search query
            
        Returns:
            List of song dictionaries
        """
        try:
            # Search tracks
            tracks_result = await self.shazam.search_track(query=query, limit=10)
            
            songs = []
            if tracks_result and tracks_result.get('tracks', {}).get('hits'):
                for hit in tracks_result['tracks']['hits']:
                    track = hit['track']
                    
                    song_info = {
                        'id': track.get('key', ''),
                        'title': track.get('title', 'Unknown'),
                        'artist': track.get('subtitle', 'Unknown'),
                        'album': track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', 'Unknown'),
                        'duration': track.get('duration', 0),
                        'image_url': track.get('images', {}).get('coverarthq', ''),
                        'spotify_url': track.get('hub', {}).get('actions', [{}])[0].get('uri', ''),
                        'apple_url': track.get('hub', {}).get('options', [{}])[0].get('actions', [{}])[0].get('uri', ''),
                        'youtube_url': track.get('hub', {}).get('options', [{}])[1].get('actions', [{}])[0].get('uri', '')
                    }
                    
                    songs.append(song_info)
            
            logger.info(f"Found {len(songs)} songs for query: {query}")
            return songs
            
        except Exception as e:
            logger.error(f"Error searching songs: {e}")
            return []
    
    async def get_track_info(self, track_id: str) -> Optional[Dict]:
        """
        Get detailed information about a track
        
        Args:
            track_id: Shazam track ID
            
        Returns:
            Dictionary with track information or None if not found
        """
        try:
            track_info = await self.shazam.track_about(track_id=track_id)
            
            if track_info:
                serialized = Serialize.track(data=track_info)
                
                # Convert to dictionary
                song_info = {
                    'title': serialized.title,
                    'artist': serialized.artist,
                    'album': serialized.album,
                    'duration': serialized.duration,
                    'genre': serialized.genre,
                    'year': serialized.year,
                    'spotify_url': serialized.spotify_url,
                    'apple_url': serialized.apple_url,
                    'youtube_url': serialized.youtube_url,
                    'image_url': serialized.image_url,
                    'shazam_id': serialized.shazam_id,
                    'isrc': serialized.isrc
                }
                
                logger.info(f"Retrieved track info for: {song_info['title']} - {song_info['artist']}")
                return song_info
            else:
                logger.info(f"No track found with ID: {track_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting track info: {e}")
            return None
    
    async def get_artist_info(self, artist_id: str) -> Optional[Dict]:
        """
        Get detailed information about an artist
        
        Args:
            artist_id: Shazam artist ID
            
        Returns:
            Dictionary with artist information or None if not found
        """
        try:
            artist_info = await self.shazam.artist_about(artist_id=artist_id)
            
            if artist_info:
                serialized = Serialize.artist(data=artist_info)
                
                # Convert to dictionary
                info = {
                    'name': serialized.name,
                    'id': serialized.id,
                    'bio': serialized.bio,
                    'genres': serialized.genres,
                    'origin': serialized.origin,
                    'formed_year': serialized.formed_year,
                    'website': serialized.website,
                    'twitter': serialized.twitter,
                    'facebook': serialized.facebook,
                    'instagram': serialized.instagram,
                    'spotify_url': serialized.spotify_url,
                    'apple_url': serialized.apple_url,
                    'image_url': serialized.image_url
                }
                
                logger.info(f"Retrieved artist info for: {info['name']}")
                return info
            else:
                logger.info(f"No artist found with ID: {artist_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting artist info: {e}")
            return None
    
    async def search_artist(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for artists by query
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of artist dictionaries
        """
        try:
            artists_result = await self.shazam.search_artist(query=query, limit=limit)
            
            artists = []
            if artists_result and artists_result.get('artists', {}).get('hits'):
                for hit in artists_result['artists']['hits']:
                    artist = hit['artist']
                    
                    artist_info = {
                        'id': artist.get('id', ''),
                        'name': artist.get('name', 'Unknown'),
                        'genre': artist.get('genres', {}).get('primary', ''),
                        'image_url': artist.get('avatar', ''),
                        'verified': artist.get('verified', False)
                    }
                    
                    artists.append(artist_info)
            
            logger.info(f"Found {len(artists)} artists for query: {query}")
            return artists
            
        except Exception as e:
            logger.error(f"Error searching artists: {e}")
            return []
    
    async def get_related_tracks(self, track_id: str, limit: int = 5, offset: int = 0) -> List[Dict]:
        """
        Get related tracks for a given track
        
        Args:
            track_id: Shazam track ID
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of related track dictionaries
        """
        try:
            related_result = await self.shazam.related_tracks(track_id=track_id, limit=limit, offset=offset)
            
            tracks = []
            if related_result and related_result.get('tracks'):
                for track in related_result['tracks']:
                    track_info = {
                        'id': track.get('key', ''),
                        'title': track.get('title', 'Unknown'),
                        'artist': track.get('subtitle', 'Unknown'),
                        'album': track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', 'Unknown'),
                        'duration': track.get('duration', 0),
                        'image_url': track.get('images', {}).get('coverarthq', ''),
                        'spotify_url': track.get('hub', {}).get('actions', [{}])[0].get('uri', ''),
                        'apple_url': track.get('hub', {}).get('options', [{}])[0].get('actions', [{}])[0].get('uri', ''),
                        'youtube_url': track.get('hub', {}).get('options', [{}])[1].get('actions', [{}])[0].get('uri', '')
                    }
                    
                    tracks.append(track_info)
            
            logger.info(f"Found {len(tracks)} related tracks for track ID: {track_id}")
            return tracks
            
        except Exception as e:
            logger.error(f"Error getting related tracks: {e}")
            return []
    
    async def get_top_tracks(self, country_code: str = None, city_name: str = None, limit: int = 10) -> List[Dict]:
        """
        Get top tracks by country or city
        
        Args:
            country_code: Country code (e.g., 'US', 'GB', 'IR')
            city_name: City name (e.g., 'London', 'Tehran')
            limit: Maximum number of results
            
        Returns:
            List of top track dictionaries
        """
        try:
            if city_name and country_code:
                # Get top city tracks
                result = await self.shazam.top_city_tracks(country_code=country_code, city_name=city_name, limit=limit)
            elif country_code:
                # Get top country tracks
                result = await self.shazam.top_country_tracks(country_code=country_code, limit=limit)
            else:
                # Get top world tracks
                result = await self.shazam.top_world_tracks(limit=limit)
            
            tracks = []
            if result and result.get('tracks'):
                for track in result['tracks']:
                    track_info = {
                        'id': track.get('key', ''),
                        'title': track.get('title', 'Unknown'),
                        'artist': track.get('subtitle', 'Unknown'),
                        'album': track.get('sections', [{}])[0].get('metadata', [{}])[0].get('text', 'Unknown'),
                        'duration': track.get('duration', 0),
                        'image_url': track.get('images', {}).get('coverarthq', ''),
                        'spotify_url': track.get('hub', {}).get('actions', [{}])[0].get('uri', ''),
                        'apple_url': track.get('hub', {}).get('options', [{}])[0].get('actions', [{}])[0].get('uri', ''),
                        'youtube_url': track.get('hub', {}).get('options', [{}])[1].get('actions', [{}])[0].get('uri', '')
                    }
                    
                    tracks.append(track_info)
            
            location = f"{city_name}, {country_code}" if city_name and country_code else country_code or "World"
            logger.info(f"Found {len(tracks)} top tracks for {location}")
            return tracks
            
        except Exception as e:
            logger.error(f"Error getting top tracks: {e}")
            return []
    
    async def get_listening_count(self, track_id: str) -> Optional[int]:
        """
        Get listening count for a track
        
        Args:
            track_id: Shazam track ID
            
        Returns:
            Listening count or None if not found
        """
        try:
            count = await self.shazam.listening_counter(track_id=track_id)
            
            if count:
                logger.info(f"Listening count for track {track_id}: {count}")
                return count
            else:
                logger.info(f"No listening count found for track: {track_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting listening count: {e}")
            return None