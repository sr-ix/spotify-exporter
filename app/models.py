"""
Pydantic models for Spotify API objects.

This module contains Pydantic models that represent Spotify API objects
such as playlists, artists, albums, and tracks.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ExternalUrls(BaseModel):
    """External URLs for a Spotify object."""

    spotify: str | None = None


class Image(BaseModel):
    """Image object for Spotify items."""

    url: str
    height: int | None = None
    width: int | None = None


class Followers(BaseModel):
    """Followers information for a user or artist."""

    href: str | None = None
    total: int = 0


class Copyright(BaseModel):
    """Copyright information for an album."""

    text: str
    type: str


class ExternalIds(BaseModel):
    """External IDs for a track or album."""

    isrc: str | None = None
    ean: str | None = None
    upc: str | None = None


class Restrictions(BaseModel):
    """Restrictions for a track or album."""

    reason: str | None = None


class ResumePoint(BaseModel):
    """Resume point for a track in a playlist."""

    fully_played: bool
    resume_position_ms: int


class Artist(BaseModel):
    """Spotify Artist object."""

    external_urls: ExternalUrls | None = None
    followers: Followers | None = None
    genres: list[str] | None = None
    href: str | None = None
    id: str
    images: list[Image] | None = None
    name: str
    popularity: int | None = Field(None, ge=0, le=100)
    type: str = "artist"
    uri: str


class SimplifiedArtist(BaseModel):
    """Simplified Artist object (used in tracks and albums)."""

    external_urls: ExternalUrls | None = None
    href: str | None = None
    id: str
    name: str
    type: str = "artist"
    uri: str


class Album(BaseModel):
    """Spotify Album object."""

    album_type: str
    artists: list[SimplifiedArtist]
    available_markets: list[str] | None = None
    external_urls: ExternalUrls | None = None
    href: str | None = None
    id: str
    images: list[Image] | None = None
    name: str
    release_date: str
    release_date_precision: str
    restrictions: Restrictions | None = None
    type: str = "album"
    uri: str
    total_tracks: int | None = None
    copyrights: list[Copyright] | None = None
    external_ids: ExternalIds | None = None
    genres: list[str] | None = None
    label: str | None = None
    popularity: int | None = Field(None, ge=0, le=100)

    @field_validator('album_type')
    @classmethod
    def validate_album_type(cls, v):
        valid_types = ['album', 'single', 'compilation']
        if v not in valid_types:
            raise ValueError(f'Album type must be one of: {valid_types}')
        return v

    @field_validator('release_date_precision')
    @classmethod
    def validate_release_date_precision(cls, v):
        valid_precisions = ['year', 'month', 'day']
        if v not in valid_precisions:
            raise ValueError(f'Release date precision must be one of: {valid_precisions}')
        return v


class SimplifiedAlbum(BaseModel):
    """Simplified Album object (used in tracks)."""

    album_type: str
    artists: list[SimplifiedArtist]
    available_markets: list[str] | None = None
    external_urls: ExternalUrls | None = None
    href: str | None = None
    id: str
    images: list[Image] | None = None
    name: str
    release_date: str
    release_date_precision: str
    restrictions: Restrictions | None = None
    type: str = "album"
    uri: str
    total_tracks: int | None = None

    @field_validator('album_type')
    @classmethod
    def validate_album_type(cls, v):
        valid_types = ['album', 'single', 'compilation']
        if v not in valid_types:
            raise ValueError(f'Album type must be one of: {valid_types}')
        return v

    @field_validator('release_date_precision')
    @classmethod
    def validate_release_date_precision(cls, v):
        valid_precisions = ['year', 'month', 'day']
        if v not in valid_precisions:
            raise ValueError(f'Release date precision must be one of: {valid_precisions}')
        return v


class Track(BaseModel):
    """Spotify Track object."""

    album: SimplifiedAlbum
    artists: list[SimplifiedArtist]
    available_markets: list[str] | None = None
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: ExternalIds | None = None
    external_urls: ExternalUrls | None = None
    href: str | None = None
    id: str
    is_playable: bool | None = None
    linked_from: Any | None = None  # TrackLink object
    restrictions: Restrictions | None = None
    name: str
    popularity: int | None = Field(None, ge=0, le=100)
    preview_url: str | None = None
    track_number: int
    type: str = "track"
    uri: str
    is_local: bool = False

    @field_validator('duration_ms')
    @classmethod
    def validate_duration_ms(cls, v):
        if v < 0:
            raise ValueError('Duration must be non-negative')
        return v

    @field_validator('disc_number')
    @classmethod
    def validate_disc_number(cls, v):
        if v < 1:
            raise ValueError('Disc number must be at least 1')
        return v

    @field_validator('track_number')
    @classmethod
    def validate_track_number(cls, v):
        if v < 1:
            raise ValueError('Track number must be at least 1')
        return v


class PlaylistOwner(BaseModel):
    """Owner of a playlist."""

    display_name: str | None = None
    external_urls: ExternalUrls | None = None
    followers: Followers | None = None
    href: str | None = None
    id: str
    images: list[Image] | None = None
    type: str = "user"
    uri: str


class PlaylistTrack(BaseModel):
    """Track object within a playlist."""

    added_at: datetime | None = None
    added_by: PlaylistOwner | None = None
    is_local: bool = False
    primary_color: str | None = None
    track: Track | None = None
    video_thumbnail: Any | None = None  # VideoThumbnail object


class PlaylistTracksRef(BaseModel):
    """Reference to playlist tracks."""

    href: str | None = None
    total: int = 0


class Playlist(BaseModel):
    """Spotify Playlist object."""

    collaborative: bool
    description: str | None = None
    external_urls: ExternalUrls | None = None
    followers: Followers | None = None
    href: str | None = None
    id: str
    images: list[Image] | None = None
    name: str
    owner: PlaylistOwner
    public: bool | None = None
    snapshot_id: str
    tracks: PlaylistTracksRef
    type: str = "playlist"
    uri: str


class PlaylistWithTracks(BaseModel):
    """Playlist object with full track information."""

    collaborative: bool
    description: str | None = None
    external_urls: ExternalUrls | None = None
    followers: Followers | None = None
    href: str | None = None
    id: str
    images: list[Image] | None = None
    name: str
    owner: PlaylistOwner
    public: bool | None = None
    snapshot_id: str
    tracks: list[PlaylistTrack]
    type: str = "playlist"
    uri: str


class PagingObject(BaseModel):
    """Generic paging object for paginated responses."""

    href: str
    items: list[Any]
    limit: int
    next: str | None = None
    offset: int
    previous: str | None = None
    total: int

    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v):
        if v < 0:
            raise ValueError('Limit must be non-negative')
        return v

    @field_validator('offset')
    @classmethod
    def validate_offset(cls, v):
        if v < 0:
            raise ValueError('Offset must be non-negative')
        return v

    @field_validator('total')
    @classmethod
    def validate_total(cls, v):
        if v < 0:
            raise ValueError('Total must be non-negative')
        return v


class PlaylistsPagingObject(PagingObject):
    """Paging object for playlists."""

    items: list[Playlist]


class TracksPagingObject(PagingObject):
    """Paging object for tracks."""

    items: list[Track]


class ArtistsPagingObject(PagingObject):
    """Paging object for artists."""

    items: list[Artist]


class AlbumsPagingObject(PagingObject):
    """Paging object for albums."""

    items: list[Album]


class AudioFeatures(BaseModel):
    """Audio features for a track."""

    acousticness: float = Field(..., ge=0.0, le=1.0)
    analysis_url: str
    danceability: float = Field(..., ge=0.0, le=1.0)
    duration_ms: int
    energy: float = Field(..., ge=0.0, le=1.0)
    id: str
    instrumentalness: float = Field(..., ge=0.0, le=1.0)
    key: int = Field(..., ge=-1, le=11)
    liveness: float = Field(..., ge=0.0, le=1.0)
    loudness: float
    mode: int = Field(..., ge=0, le=1)
    speechiness: float = Field(..., ge=0.0, le=1.0)
    tempo: float
    time_signature: int = Field(..., ge=3, le=7)
    track_href: str
    type: str = "audio_features"
    uri: str
    valence: float = Field(..., ge=0.0, le=1.0)

    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v):
        if v not in [0, 1]:
            raise ValueError('Mode must be 0 or 1')
        return v

    @field_validator('time_signature')
    @classmethod
    def validate_time_signature(cls, v):
        if v < 3 or v > 7:
            raise ValueError('Time signature must be between 3 and 7')
        return v


class AudioAnalysis(BaseModel):
    """Audio analysis for a track."""

    bars: list[Any] = []  # TimeInterval objects
    beats: list[Any] = []  # TimeInterval objects
    sections: list[Any] = []  # Section objects
    segments: list[Any] = []  # Segment objects
    tatums: list[Any] = []  # TimeInterval objects


class Category(BaseModel):
    """Category object for browse categories."""

    href: str
    icons: list[Image]
    id: str
    name: str


class CategoriesPagingObject(PagingObject):
    """Paging object for categories."""

    items: list[Category]


class SearchResult(BaseModel):
    """Search result object."""

    tracks: TracksPagingObject | None = None
    artists: ArtistsPagingObject | None = None
    albums: AlbumsPagingObject | None = None
    playlists: PlaylistsPagingObject | None = None
    shows: Any | None = None  # ShowsPagingObject
    episodes: Any | None = None  # EpisodesPagingObject
    audiobooks: Any | None = None  # AudiobooksPagingObject


class UserProfile(BaseModel):
    """User profile object."""

    country: str | None = None
    display_name: str | None = None
    email: str | None = None
    explicit_content: Any | None = None  # ExplicitContentSettings
    external_urls: ExternalUrls | None = None
    followers: Followers | None = None
    href: str | None = None
    id: str
    images: list[Image] | None = None
    product: str | None = None
    type: str = "user"
    uri: str
