"""
Spotify client wrapper with Pydantic models.

This module provides a type-safe wrapper around the Spotify API
using Pydantic models for data validation and serialization.
"""

import spotipy

from app.models import (
    Album,
    Artist,
    AudioFeatures,
    Playlist,
    PlaylistWithTracks,
    SearchResult,
    Track,
    TracksPagingObject,
    UserProfile,
)


class SpotifyClient:
    """
    Type-safe Spotify client wrapper.

    This class wraps the spotipy client and provides methods that return
    validated Pydantic models instead of raw dictionaries.
    """

    def __init__(self, spotify_client: spotipy.Spotify):
        """
        Initialize the Spotify client wrapper.

        Args:
            spotify_client: Authenticated spotipy client instance
        """
        self.client = spotify_client

    def get_current_user(self) -> UserProfile:
        """
        Get the current user's profile.

        Returns:
            UserProfile object
        """
        user_data = self.client.current_user()
        return UserProfile(**user_data)

    def get_user_playlists(self, user_id: str, limit: int = 20, offset: int = 0) -> list[Playlist]:
        """
        Get a user's playlists.

        Args:
            user_id: Spotify user ID
            limit: Number of playlists to return (max 50)
            offset: Offset for pagination

        Returns:
            List of Playlist objects
        """
        playlists_data = self.client.user_playlists(user_id, limit=limit, offset=offset)
        return [Playlist(**playlist) for playlist in playlists_data['items']]

    def get_playlist(self, playlist_id: str, fields: str | None = None) -> Playlist:
        """
        Get a playlist by ID.

        Args:
            playlist_id: Spotify playlist ID
            fields: Comma-separated list of fields to return

        Returns:
            Playlist object
        """
        playlist_data = self.client.playlist(playlist_id, fields=fields)
        return Playlist(**playlist_data)

    def get_playlist_tracks(self, playlist_id: str, limit: int = 100, offset: int = 0) -> TracksPagingObject:
        """
        Get tracks from a playlist.

        Args:
            playlist_id: Spotify playlist ID
            limit: Number of tracks to return (max 100)
            offset: Offset for pagination

        Returns:
            TracksPagingObject with Track objects
        """
        tracks_data = self.client.playlist_tracks(playlist_id, limit=limit, offset=offset)
        return TracksPagingObject(**tracks_data)

    def get_playlist_with_tracks(self, playlist_id: str) -> PlaylistWithTracks:
        """
        Get a playlist with all its tracks.

        Args:
            playlist_id: Spotify playlist ID

        Returns:
            PlaylistWithTracks object
        """
        playlist_data = self.client.playlist(playlist_id)
        return PlaylistWithTracks(**playlist_data)

    def get_track(self, track_id: str) -> Track:
        """
        Get a track by ID.

        Args:
            track_id: Spotify track ID

        Returns:
            Track object
        """
        track_data = self.client.track(track_id)
        return Track(**track_data)

    def get_tracks(self, track_ids: list[str]) -> list[Track]:
        """
        Get multiple tracks by IDs.

        Args:
            track_ids: List of Spotify track IDs

        Returns:
            List of Track objects
        """
        tracks_data = self.client.tracks(track_ids)
        return [Track(**track) for track in tracks_data['tracks']]

    def get_album(self, album_id: str) -> Album:
        """
        Get an album by ID.

        Args:
            album_id: Spotify album ID

        Returns:
            Album object
        """
        album_data = self.client.album(album_id)
        return Album(**album_data)

    def get_album_tracks(self, album_id: str, limit: int = 20, offset: int = 0) -> TracksPagingObject:
        """
        Get tracks from an album.

        Args:
            album_id: Spotify album ID
            limit: Number of tracks to return (max 50)
            offset: Offset for pagination

        Returns:
            TracksPagingObject with Track objects
        """
        tracks_data = self.client.album_tracks(album_id, limit=limit, offset=offset)
        return TracksPagingObject(**tracks_data)

    def get_artist(self, artist_id: str) -> Artist:
        """
        Get an artist by ID.

        Args:
            artist_id: Spotify artist ID

        Returns:
            Artist object
        """
        artist_data = self.client.artist(artist_id)
        return Artist(**artist_data)

    def get_artist_albums(self, artist_id: str, album_type: str | None = None,
                         limit: int = 20, offset: int = 0) -> list[Album]:
        """
        Get albums by an artist.

        Args:
            artist_id: Spotify artist ID
            album_type: Type of albums to return (album, single, compilation)
            limit: Number of albums to return (max 50)
            offset: Offset for pagination

        Returns:
            List of Album objects
        """
        albums_data = self.client.artist_albums(artist_id, album_type=album_type,
                                               limit=limit, offset=offset)
        return [Album(**album) for album in albums_data['items']]

    def get_artist_top_tracks(self, artist_id: str, country: str = 'US') -> list[Track]:
        """
        Get an artist's top tracks.

        Args:
            artist_id: Spotify artist ID
            country: Country code for market

        Returns:
            List of Track objects
        """
        tracks_data = self.client.artist_top_tracks(artist_id, country=country)
        return [Track(**track) for track in tracks_data['tracks']]

    def get_audio_features(self, track_id: str) -> AudioFeatures:
        """
        Get audio features for a track.

        Args:
            track_id: Spotify track ID

        Returns:
            AudioFeatures object
        """
        features_data = self.client.audio_features(track_id)
        if features_data:
            return AudioFeatures(**features_data[0])
        raise ValueError(f"No audio features found for track {track_id}")

    def get_audio_features_multiple(self, track_ids: list[str]) -> list[AudioFeatures]:
        """
        Get audio features for multiple tracks.

        Args:
            track_ids: List of Spotify track IDs

        Returns:
            List of AudioFeatures objects
        """
        features_data = self.client.audio_features(track_ids)
        return [AudioFeatures(**features) for features in features_data if features]

    def search(self, q: str, type: str = 'track', limit: int = 20, offset: int = 0) -> SearchResult:
        """
        Search for tracks, artists, albums, or playlists.

        Args:
            q: Search query
            type: Type of search (track, artist, album, playlist)
            limit: Number of results to return (max 50)
            offset: Offset for pagination

        Returns:
            SearchResult object
        """
        search_data = self.client.search(q, type=type, limit=limit, offset=offset)
        return SearchResult(**search_data)

    def get_user_top_tracks(self, limit: int = 20, offset: int = 0,
                           time_range: str = 'medium_term') -> list[Track]:
        """
        Get user's top tracks.

        Args:
            limit: Number of tracks to return (max 50)
            offset: Offset for pagination
            time_range: Time range (short_term, medium_term, long_term)

        Returns:
            List of Track objects
        """
        tracks_data = self.client.current_user_top_tracks(limit=limit, offset=offset,
                                                         time_range=time_range)
        return [Track(**track) for track in tracks_data['items']]

    def get_user_top_artists(self, limit: int = 20, offset: int = 0,
                            time_range: str = 'medium_term') -> list[Artist]:
        """
        Get user's top artists.

        Args:
            limit: Number of artists to return (max 50)
            offset: Offset for pagination
            time_range: Time range (short_term, medium_term, long_term)

        Returns:
            List of Artist objects
        """
        artists_data = self.client.current_user_top_artists(limit=limit, offset=offset,
                                                           time_range=time_range)
        return [Artist(**artist) for artist in artists_data['items']]

    def get_recommendations(self, seed_artists: list[str] | None = None,
                           seed_genres: list[str] | None = None,
                           seed_tracks: list[str] | None = None,
                           limit: int = 20, **kwargs) -> list[Track]:
        """
        Get track recommendations.

        Args:
            seed_artists: List of artist IDs to seed recommendations
            seed_genres: List of genres to seed recommendations
            seed_tracks: List of track IDs to seed recommendations
            limit: Number of recommendations to return (max 100)
            **kwargs: Additional parameters for recommendations

        Returns:
            List of Track objects
        """
        recommendations_data = self.client.recommendations(
            seed_artists=seed_artists,
            seed_genres=seed_genres,
            seed_tracks=seed_tracks,
            limit=limit,
            **kwargs
        )
        return [Track(**track) for track in recommendations_data['tracks']]

    def create_playlist(self, user_id: str, name: str, description: str = "",
                       public: bool = True) -> Playlist:
        """
        Create a new playlist.

        Args:
            user_id: Spotify user ID
            name: Playlist name
            description: Playlist description
            public: Whether the playlist is public

        Returns:
            Playlist object
        """
        playlist_data = self.client.user_playlist_create(
            user_id, name, description=description, public=public
        )
        return Playlist(**playlist_data)

    def add_tracks_to_playlist(self, playlist_id: str, track_uris: list[str],
                              position: int | None = None) -> str:
        """
        Add tracks to a playlist.

        Args:
            playlist_id: Spotify playlist ID
            track_uris: List of track URIs to add
            position: Position to insert tracks (None for end)

        Returns:
            Snapshot ID
        """
        result = self.client.playlist_add_items(playlist_id, track_uris, position=position)
        return result['snapshot_id']

    def remove_tracks_from_playlist(self, playlist_id: str, track_uris: list[str]) -> str:
        """
        Remove tracks from a playlist.

        Args:
            playlist_id: Spotify playlist ID
            track_uris: List of track URIs to remove

        Returns:
            Snapshot ID
        """
        result = self.client.playlist_remove_all_occurrences_of_items(playlist_id, track_uris)
        return result['snapshot_id']
