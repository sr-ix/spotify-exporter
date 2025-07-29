"""
Tests for the Pydantic models.

This module contains tests for the Spotify API Pydantic models,
ensuring they correctly validate and parse Spotify API responses.
"""


import pytest
from pydantic import ValidationError

from app.models import (
    Album,
    Artist,
    AudioFeatures,
    ExternalIds,
    ExternalUrls,
    Followers,
    Image,
    Playlist,
    PlaylistOwner,
    PlaylistTrack,
    PlaylistTracksRef,
    SimplifiedAlbum,
    SimplifiedArtist,
    Track,
    TracksPagingObject,
    UserProfile,
)


class TestBasicModels:
    """Test basic utility models."""

    def test_external_urls(self):
        """Test ExternalUrls model."""
        data = {"spotify": "https://open.spotify.com/artist/123"}
        urls = ExternalUrls(**data)
        assert urls.spotify == "https://open.spotify.com/artist/123"

    def test_external_urls_empty(self):
        """Test ExternalUrls model with empty data."""
        urls = ExternalUrls()
        assert urls.spotify is None

    def test_image(self):
        """Test Image model."""
        data = {
            "url": "https://i.scdn.co/image/123",
            "height": 640,
            "width": 640
        }
        image = Image(**data)
        assert image.url == "https://i.scdn.co/image/123"
        assert image.height == 640
        assert image.width == 640

    def test_image_minimal(self):
        """Test Image model with minimal data."""
        data = {"url": "https://i.scdn.co/image/123"}
        image = Image(**data)
        assert image.url == "https://i.scdn.co/image/123"
        assert image.height is None
        assert image.width is None

    def test_followers(self):
        """Test Followers model."""
        data = {"href": "https://api.spotify.com/v1/artists/123/followers", "total": 1000}
        followers = Followers(**data)
        assert followers.href == "https://api.spotify.com/v1/artists/123/followers"
        assert followers.total == 1000

    def test_followers_minimal(self):
        """Test Followers model with minimal data."""
        followers = Followers()
        assert followers.href is None
        assert followers.total == 0

    def test_external_ids(self):
        """Test ExternalIds model."""
        data = {
            "isrc": "USRC12345678",
            "ean": "1234567890123",
            "upc": "123456789012"
        }
        external_ids = ExternalIds(**data)
        assert external_ids.isrc == "USRC12345678"
        assert external_ids.ean == "1234567890123"
        assert external_ids.upc == "123456789012"


class TestArtistModels:
    """Test Artist-related models."""

    def test_simplified_artist(self):
        """Test SimplifiedArtist model."""
        data = {
            "external_urls": {"spotify": "https://open.spotify.com/artist/123"},
            "href": "https://api.spotify.com/v1/artists/123",
            "id": "123",
            "name": "Test Artist",
            "type": "artist",
            "uri": "spotify:artist:123"
        }
        artist = SimplifiedArtist(**data)
        assert artist.id == "123"
        assert artist.name == "Test Artist"
        assert artist.type == "artist"
        assert artist.uri == "spotify:artist:123"

    def test_artist_full(self):
        """Test full Artist model."""
        data = {
            "external_urls": {"spotify": "https://open.spotify.com/artist/123"},
            "followers": {"href": None, "total": 1000},
            "genres": ["rock", "alternative"],
            "href": "https://api.spotify.com/v1/artists/123",
            "id": "123",
            "images": [
                {
                    "url": "https://i.scdn.co/image/123",
                    "height": 640,
                    "width": 640
                }
            ],
            "name": "Test Artist",
            "popularity": 85,
            "type": "artist",
            "uri": "spotify:artist:123"
        }
        artist = Artist(**data)
        assert artist.id == "123"
        assert artist.name == "Test Artist"
        assert artist.popularity == 85
        assert artist.genres == ["rock", "alternative"]
        assert len(artist.images) == 1
        assert artist.followers.total == 1000

    def test_artist_popularity_validation(self):
        """Test Artist popularity validation."""
        data = {
            "id": "123",
            "name": "Test Artist",
            "type": "artist",
            "uri": "spotify:artist:123",
            "popularity": 101  # Invalid
        }
        with pytest.raises(ValidationError):
            Artist(**data)

    def test_artist_popularity_negative(self):
        """Test Artist popularity validation with negative value."""
        data = {
            "id": "123",
            "name": "Test Artist",
            "type": "artist",
            "uri": "spotify:artist:123",
            "popularity": -1  # Invalid
        }
        with pytest.raises(ValidationError):
            Artist(**data)


class TestAlbumModels:
    """Test Album-related models."""

    def test_simplified_album(self):
        """Test SimplifiedAlbum model."""
        data = {
            "album_type": "album",
            "artists": [
                {
                    "external_urls": {"spotify": "https://open.spotify.com/artist/123"},
                    "href": "https://api.spotify.com/v1/artists/123",
                    "id": "123",
                    "name": "Test Artist",
                    "type": "artist",
                    "uri": "spotify:artist:123"
                }
            ],
            "available_markets": ["US", "GB"],
            "external_urls": {"spotify": "https://open.spotify.com/album/456"},
            "href": "https://api.spotify.com/v1/albums/456",
            "id": "456",
            "images": [
                {
                    "url": "https://i.scdn.co/image/456",
                    "height": 640,
                    "width": 640
                }
            ],
            "name": "Test Album",
            "release_date": "2023-01-01",
            "release_date_precision": "day",
            "type": "album",
            "uri": "spotify:album:456",
            "total_tracks": 12
        }
        album = SimplifiedAlbum(**data)
        assert album.id == "456"
        assert album.name == "Test Album"
        assert album.album_type == "album"
        assert album.release_date == "2023-01-01"
        assert album.release_date_precision == "day"
        assert album.total_tracks == 12
        assert len(album.artists) == 1
        assert album.artists[0].name == "Test Artist"

    def test_album_full(self):
        """Test full Album model."""
        data = {
            "album_type": "album",
            "artists": [
                {
                    "external_urls": {"spotify": "https://open.spotify.com/artist/123"},
                    "href": "https://api.spotify.com/v1/artists/123",
                    "id": "123",
                    "name": "Test Artist",
                    "type": "artist",
                    "uri": "spotify:artist:123"
                }
            ],
            "available_markets": ["US", "GB"],
            "external_urls": {"spotify": "https://open.spotify.com/album/456"},
            "href": "https://api.spotify.com/v1/albums/456",
            "id": "456",
            "images": [
                {
                    "url": "https://i.scdn.co/image/456",
                    "height": 640,
                    "width": 640
                }
            ],
            "name": "Test Album",
            "release_date": "2023-01-01",
            "release_date_precision": "day",
            "type": "album",
            "uri": "spotify:album:456",
            "total_tracks": 12,
            "copyrights": [
                {
                    "text": "© 2023 Test Label",
                    "type": "C"
                }
            ],
            "external_ids": {
                "isrc": "USRC12345678",
                "upc": "123456789012"
            },
            "genres": ["rock", "alternative"],
            "label": "Test Label",
            "popularity": 75
        }
        album = Album(**data)
        assert album.id == "456"
        assert album.name == "Test Album"
        assert album.popularity == 75
        assert album.label == "Test Label"
        assert album.genres == ["rock", "alternative"]
        assert len(album.copyrights) == 1
        assert album.copyrights[0].text == "© 2023 Test Label"

    def test_album_type_validation(self):
        """Test Album type validation."""
        data = {
            "album_type": "invalid_type",
            "artists": [
                {
                    "id": "123",
                    "name": "Test Artist",
                    "type": "artist",
                    "uri": "spotify:artist:123"
                }
            ],
            "id": "456",
            "name": "Test Album",
            "release_date": "2023-01-01",
            "release_date_precision": "day",
            "type": "album",
            "uri": "spotify:album:456"
        }
        with pytest.raises(ValueError, match="Album type must be one of"):
            Album(**data)

    def test_album_release_date_precision_validation(self):
        """Test Album release date precision validation."""
        data = {
            "album_type": "album",
            "artists": [
                {
                    "id": "123",
                    "name": "Test Artist",
                    "type": "artist",
                    "uri": "spotify:artist:123"
                }
            ],
            "id": "456",
            "name": "Test Album",
            "release_date": "2023-01-01",
            "release_date_precision": "invalid",
            "type": "album",
            "uri": "spotify:album:456"
        }
        with pytest.raises(ValueError, match="Release date precision must be one of"):
            Album(**data)


class TestTrackModels:
    """Test Track-related models."""

    def test_track(self):
        """Test Track model."""
        data = {
            "album": {
                "album_type": "album",
                "artists": [
                    {
                        "external_urls": {"spotify": "https://open.spotify.com/artist/123"},
                        "href": "https://api.spotify.com/v1/artists/123",
                        "id": "123",
                        "name": "Test Artist",
                        "type": "artist",
                        "uri": "spotify:artist:123"
                    }
                ],
                "external_urls": {"spotify": "https://open.spotify.com/album/456"},
                "href": "https://api.spotify.com/v1/albums/456",
                "id": "456",
                "images": [
                    {
                        "url": "https://i.scdn.co/image/456",
                        "height": 640,
                        "width": 640
                    }
                ],
                "name": "Test Album",
                "release_date": "2023-01-01",
                "release_date_precision": "day",
                "type": "album",
                "uri": "spotify:album:456"
            },
            "artists": [
                {
                    "external_urls": {"spotify": "https://open.spotify.com/artist/123"},
                    "href": "https://api.spotify.com/v1/artists/123",
                    "id": "123",
                    "name": "Test Artist",
                    "type": "artist",
                    "uri": "spotify:artist:123"
                }
            ],
            "available_markets": ["US", "GB"],
            "disc_number": 1,
            "duration_ms": 180000,
            "explicit": False,
            "external_ids": {"isrc": "USRC12345678"},
            "external_urls": {"spotify": "https://open.spotify.com/track/789"},
            "href": "https://api.spotify.com/v1/tracks/789",
            "id": "789",
            "name": "Test Track",
            "popularity": 80,
            "preview_url": "https://p.scdn.co/mp3-preview/789",
            "track_number": 1,
            "type": "track",
            "uri": "spotify:track:789",
            "is_local": False
        }
        track = Track(**data)
        assert track.id == "789"
        assert track.name == "Test Track"
        assert track.popularity == 80
        assert track.duration_ms == 180000
        assert track.disc_number == 1
        assert track.track_number == 1
        assert track.explicit is False
        assert track.is_local is False
        assert track.album.name == "Test Album"
        assert len(track.artists) == 1
        assert track.artists[0].name == "Test Artist"

    def test_track_validation(self):
        """Test Track validation."""
        data = {
            "album": {
                "album_type": "album",
                "artists": [
                    {
                        "id": "123",
                        "name": "Test Artist",
                        "type": "artist",
                        "uri": "spotify:artist:123"
                    }
                ],
                "id": "456",
                "name": "Test Album",
                "release_date": "2023-01-01",
                "release_date_precision": "day",
                "type": "album",
                "uri": "spotify:album:456"
            },
            "artists": [
                {
                    "id": "123",
                    "name": "Test Artist",
                    "type": "artist",
                    "uri": "spotify:artist:123"
                }
            ],
            "disc_number": 0,  # Invalid
            "duration_ms": 180000,
            "explicit": False,
            "id": "789",
            "name": "Test Track",
            "track_number": 1,
            "type": "track",
            "uri": "spotify:track:789"
        }
        with pytest.raises(ValueError, match="Disc number must be at least 1"):
            Track(**data)

    def test_track_duration_validation(self):
        """Test Track duration validation."""
        data = {
            "album": {
                "album_type": "album",
                "artists": [
                    {
                        "id": "123",
                        "name": "Test Artist",
                        "type": "artist",
                        "uri": "spotify:artist:123"
                    }
                ],
                "id": "456",
                "name": "Test Album",
                "release_date": "2023-01-01",
                "release_date_precision": "day",
                "type": "album",
                "uri": "spotify:album:456"
            },
            "artists": [
                {
                    "id": "123",
                    "name": "Test Artist",
                    "type": "artist",
                    "uri": "spotify:artist:123"
                }
            ],
            "disc_number": 1,
            "duration_ms": -1000,  # Invalid
            "explicit": False,
            "id": "789",
            "name": "Test Track",
            "track_number": 1,
            "type": "track",
            "uri": "spotify:track:789"
        }
        with pytest.raises(ValueError, match="Duration must be non-negative"):
            Track(**data)


class TestPlaylistModels:
    """Test Playlist-related models."""

    def test_playlist_owner(self):
        """Test PlaylistOwner model."""
        data = {
            "display_name": "Test User",
            "external_urls": {"spotify": "https://open.spotify.com/user/123"},
            "followers": {"href": None, "total": 500},
            "href": "https://api.spotify.com/v1/users/123",
            "id": "123",
            "images": [
                {
                    "url": "https://i.scdn.co/image/123",
                    "height": 640,
                    "width": 640
                }
            ],
            "type": "user",
            "uri": "spotify:user:123"
        }
        owner = PlaylistOwner(**data)
        assert owner.id == "123"
        assert owner.display_name == "Test User"
        assert owner.type == "user"
        assert owner.followers.total == 500

    def test_playlist_tracks_ref(self):
        """Test PlaylistTracksRef model."""
        data = {
            "href": "https://api.spotify.com/v1/playlists/123/tracks",
            "total": 25
        }
        tracks_ref = PlaylistTracksRef(**data)
        assert tracks_ref.href == "https://api.spotify.com/v1/playlists/123/tracks"
        assert tracks_ref.total == 25

    def test_playlist(self):
        """Test Playlist model."""
        data = {
            "collaborative": False,
            "description": "A test playlist",
            "external_urls": {"spotify": "https://open.spotify.com/playlist/123"},
            "followers": {"href": None, "total": 100},
            "href": "https://api.spotify.com/v1/playlists/123",
            "id": "123",
            "images": [
                {
                    "url": "https://i.scdn.co/image/123",
                    "height": 640,
                    "width": 640
                }
            ],
            "name": "Test Playlist",
            "owner": {
                "display_name": "Test User",
                "external_urls": {"spotify": "https://open.spotify.com/user/456"},
                "followers": {"href": None, "total": 500},
                "href": "https://api.spotify.com/v1/users/456",
                "id": "456",
                "images": [],
                "type": "user",
                "uri": "spotify:user:456"
            },
            "public": True,
            "snapshot_id": "snapshot_123",
            "tracks": {
                "href": "https://api.spotify.com/v1/playlists/123/tracks",
                "total": 25
            },
            "type": "playlist",
            "uri": "spotify:playlist:123"
        }
        playlist = Playlist(**data)
        assert playlist.id == "123"
        assert playlist.name == "Test Playlist"
        assert playlist.collaborative is False
        assert playlist.public is True
        assert playlist.description == "A test playlist"
        assert playlist.owner.id == "456"
        assert playlist.tracks.total == 25

    def test_playlist_track(self):
        """Test PlaylistTrack model."""
        data = {
            "added_at": "2023-01-01T00:00:00Z",
            "added_by": {
                "display_name": "Test User",
                "external_urls": {"spotify": "https://open.spotify.com/user/456"},
                "followers": {"href": None, "total": 500},
                "href": "https://api.spotify.com/v1/users/456",
                "id": "456",
                "images": [],
                "type": "user",
                "uri": "spotify:user:456"
            },
            "is_local": False,
            "primary_color": "#1DB954",
            "track": {
                "album": {
                    "album_type": "album",
                    "artists": [
                        {
                            "id": "123",
                            "name": "Test Artist",
                            "type": "artist",
                            "uri": "spotify:artist:123"
                        }
                    ],
                    "id": "456",
                    "name": "Test Album",
                    "release_date": "2023-01-01",
                    "release_date_precision": "day",
                    "type": "album",
                    "uri": "spotify:album:456"
                },
                "artists": [
                    {
                        "id": "123",
                        "name": "Test Artist",
                        "type": "artist",
                        "uri": "spotify:artist:123"
                    }
                ],
                "disc_number": 1,
                "duration_ms": 180000,
                "explicit": False,
                "id": "789",
                "name": "Test Track",
                "track_number": 1,
                "type": "track",
                "uri": "spotify:track:789"
            }
        }
        playlist_track = PlaylistTrack(**data)
        assert playlist_track.is_local is False
        assert playlist_track.primary_color == "#1DB954"
        assert playlist_track.track.name == "Test Track"
        assert playlist_track.added_by.id == "456"


class TestAudioFeatures:
    """Test AudioFeatures model."""

    def test_audio_features(self):
        """Test AudioFeatures model."""
        data = {
            "acousticness": 0.5,
            "analysis_url": "https://api.spotify.com/v1/audio-analysis/789",
            "danceability": 0.7,
            "duration_ms": 180000,
            "energy": 0.8,
            "id": "789",
            "instrumentalness": 0.1,
            "key": 5,
            "liveness": 0.2,
            "loudness": -10.0,
            "mode": 1,
            "speechiness": 0.05,
            "tempo": 120.0,
            "time_signature": 4,
            "track_href": "https://api.spotify.com/v1/tracks/789",
            "type": "audio_features",
            "uri": "spotify:track:789",
            "valence": 0.6
        }
        features = AudioFeatures(**data)
        assert features.id == "789"
        assert features.acousticness == 0.5
        assert features.danceability == 0.7
        assert features.energy == 0.8
        assert features.key == 5
        assert features.mode == 1
        assert features.time_signature == 4
        assert features.tempo == 120.0
        assert features.loudness == -10.0

    def test_audio_features_validation(self):
        """Test AudioFeatures validation."""
        data = {
            "acousticness": 1.5,  # Invalid
            "analysis_url": "https://api.spotify.com/v1/audio-analysis/789",
            "danceability": 0.7,
            "duration_ms": 180000,
            "energy": 0.8,
            "id": "789",
            "instrumentalness": 0.1,
            "key": 5,
            "liveness": 0.2,
            "loudness": -10.0,
            "mode": 1,
            "speechiness": 0.05,
            "tempo": 120.0,
            "time_signature": 4,
            "track_href": "https://api.spotify.com/v1/tracks/789",
            "type": "audio_features",
            "uri": "spotify:track:789",
            "valence": 0.6
        }
        with pytest.raises(ValidationError):
            AudioFeatures(**data)

    def test_audio_features_key_validation(self):
        """Test AudioFeatures key validation."""
        data = {
            "acousticness": 0.5,
            "analysis_url": "https://api.spotify.com/v1/audio-analysis/789",
            "danceability": 0.7,
            "duration_ms": 180000,
            "energy": 0.8,
            "id": "789",
            "instrumentalness": 0.1,
            "key": 12,  # Invalid
            "liveness": 0.2,
            "loudness": -10.0,
            "mode": 1,
            "speechiness": 0.05,
            "tempo": 120.0,
            "time_signature": 4,
            "track_href": "https://api.spotify.com/v1/tracks/789",
            "type": "audio_features",
            "uri": "spotify:track:789",
            "valence": 0.6
        }
        with pytest.raises(ValidationError):
            AudioFeatures(**data)


class TestUserProfile:
    """Test UserProfile model."""

    def test_user_profile(self):
        """Test UserProfile model."""
        data = {
            "country": "US",
            "display_name": "Test User",
            "email": "test@example.com",
            "external_urls": {"spotify": "https://open.spotify.com/user/123"},
            "followers": {"href": None, "total": 500},
            "href": "https://api.spotify.com/v1/users/123",
            "id": "123",
            "images": [
                {
                    "url": "https://i.scdn.co/image/123",
                    "height": 640,
                    "width": 640
                }
            ],
            "product": "premium",
            "type": "user",
            "uri": "spotify:user:123"
        }
        user = UserProfile(**data)
        assert user.id == "123"
        assert user.display_name == "Test User"
        assert user.email == "test@example.com"
        assert user.country == "US"
        assert user.product == "premium"
        assert user.followers.total == 500


class TestPagingObjects:
    """Test paging objects."""

    def test_tracks_paging_object(self):
        """Test TracksPagingObject."""
        data = {
            "href": "https://api.spotify.com/v1/playlists/123/tracks",
            "items": [
                {
                    "album": {
                        "album_type": "album",
                        "artists": [
                            {
                                "id": "123",
                                "name": "Test Artist",
                                "type": "artist",
                                "uri": "spotify:artist:123"
                            }
                        ],
                        "id": "456",
                        "name": "Test Album",
                        "release_date": "2023-01-01",
                        "release_date_precision": "day",
                        "type": "album",
                        "uri": "spotify:album:456"
                    },
                    "artists": [
                        {
                            "id": "123",
                            "name": "Test Artist",
                            "type": "artist",
                            "uri": "spotify:artist:123"
                        }
                    ],
                    "disc_number": 1,
                    "duration_ms": 180000,
                    "explicit": False,
                    "id": "789",
                    "name": "Test Track",
                    "track_number": 1,
                    "type": "track",
                    "uri": "spotify:track:789"
                }
            ],
            "limit": 20,
            "next": "https://api.spotify.com/v1/playlists/123/tracks?offset=20",
            "offset": 0,
            "previous": None,
            "total": 25
        }
        paging = TracksPagingObject(**data)
        assert paging.href == "https://api.spotify.com/v1/playlists/123/tracks"
        assert paging.limit == 20
        assert paging.offset == 0
        assert paging.total == 25
        assert len(paging.items) == 1
        assert paging.items[0].name == "Test Track"
        assert paging.next == "https://api.spotify.com/v1/playlists/123/tracks?offset=20"
        assert paging.previous is None
