# Spotify Exporter

A Python application for authenticating with the Spotify Web API using PKCE (Proof Key for Code Exchange) with the `spotipy` library. This project provides a secure, type-safe interface for interacting with Spotify's API.

## Features

- 🔐 **PKCE Authentication**: Secure OAuth 2.0 flow using PKCE (Proof Key for Code Exchange)
- 🛡️ **No Client Secret Required**: Uses PKCE flow which is recommended for public clients
- 🧪 **Comprehensive Testing**: 69 tests covering all authentication flows and edge cases
- ⚙️ **Easy Configuration**: Simple environment-based configuration
- 🖥️ **CLI Interface**: Command-line interface for easy authentication
- 🐍 **Modern Python**: Built with Python 3.13+ and modern tooling
- 📊 **Type-Safe Models**: Pydantic models for all Spotify API objects
- 🔧 **Type-Safe Client**: Wrapper around spotipy with validated Pydantic models

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd spotify-exporter
```

2. Install dependencies using `uv`:
```bash
uv sync
```

3. Set up your environment:
```bash
uv run python main.py setup
```

4. Edit the `.env` file with your Spotify credentials (see [Getting Spotify Credentials](#getting-spotify-credentials))

## Getting Spotify Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in the app details:
   - **App name**: Your app name
   - **App description**: Description of your app
   - **Website**: Your website (optional)
   - **Redirect URI**: `http://localhost:8080/callback` (for local development)
5. Accept the terms and create the app
6. Copy the **Client ID** from your app dashboard
7. Edit the `.env` file and replace `your_client_id_here` with your actual Client ID

## Usage

### CLI Usage

1. **Setup** (creates .env template):
```bash
uv run python main.py setup
```

2. **Authenticate**:
```bash
uv run python main.py auth
```

3. Follow the prompts to complete authentication

### Programmatic Usage

#### Basic Authentication

```python
from app.spotify_auth import SpotifyAuthManager

# Initialize auth manager
auth_manager = SpotifyAuthManager(
    client_id="your_client_id",
    redirect_uri="http://localhost:8080/callback",
    scope="user-read-private user-read-email"
)

# Start authentication flow
auth_url = auth_manager.start_auth_flow()
print(f"Visit this URL: {auth_url}")

# Complete authentication (after user authorizes)
redirect_url = "http://localhost:8080/callback?code=...&state=..."
spotify_client = auth_manager.complete_auth_flow(redirect_url)
```

#### Type-Safe API Usage

```python
from app.spotify_auth import SpotifyAuthManager
from app.spotify_client import SpotifyClient

# Authenticate (as shown above)
auth_manager = SpotifyAuthManager(...)
spotify_client_raw = auth_manager.complete_auth_flow(redirect_url)

# Create type-safe client
spotify_client = SpotifyClient(spotify_client_raw)

# Get user profile (returns UserProfile Pydantic model)
user = spotify_client.get_current_user()
print(f"Authenticated as: {user.display_name} ({user.email})")

# Get user's top tracks (returns list of Track Pydantic models)
top_tracks = spotify_client.get_user_top_tracks(limit=5)
for track in top_tracks:
    print(f"{track.name} - {track.artists[0].name}")
    print(f"  Album: {track.album.name}")
    print(f"  Duration: {track.duration_ms // 1000}s")
    print(f"  Popularity: {track.popularity}")

# Search for tracks (returns SearchResult Pydantic model)
search_results = spotify_client.search("The Beatles", type="track", limit=3)
if search_results.tracks:
    for track in search_results.tracks.items:
        print(f"{track.name} - {track.artists[0].name}")

# Get audio features (returns AudioFeatures Pydantic model)
if top_tracks:
    features = spotify_client.get_audio_features(top_tracks[0].id)
    print(f"Danceability: {features.danceability}")
    print(f"Energy: {features.energy}")
    print(f"Tempo: {features.tempo} BPM")
```

## Advanced Usage

### Working with Pydantic Models

The application provides comprehensive Pydantic models for all Spotify API objects:

```python
from app.models import Track, Artist, Album, Playlist, AudioFeatures

# All models include validation and type hints
track = Track(
    id="123",
    name="Test Track",
    # ... other fields
)

# Models can be easily serialized/deserialized
track_dict = track.model_dump()
track_json = track.model_dump_json()

# Validation ensures data integrity
try:
    invalid_track = Track(
        id="123",
        name="Test Track",
        popularity=101  # Invalid: must be 0-100
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Available Models

- **Basic Models**: `ExternalUrls`, `Image`, `Followers`, `ExternalIds`, `Restrictions`
- **Artist Models**: `Artist`, `SimplifiedArtist`
- **Album Models**: `Album`, `SimplifiedAlbum`
- **Track Models**: `Track`, `PlaylistTrack`
- **Playlist Models**: `Playlist`, `PlaylistWithTracks`, `PlaylistOwner`, `PlaylistTracksRef`
- **Audio Models**: `AudioFeatures`, `AudioAnalysis`
- **User Models**: `UserProfile`
- **Paging Models**: `PagingObject`, `TracksPagingObject`, `ArtistsPagingObject`, etc.
- **Search Models**: `SearchResult`

### Type-Safe Client Methods

The `SpotifyClient` provides type-safe methods for all major Spotify API endpoints:

#### User Data
- `get_current_user() -> UserProfile`
- `get_user_top_tracks() -> list[Track]`
- `get_user_top_artists() -> list[Artist]`
- `get_user_playlists() -> list[Playlist]`

#### Tracks & Albums
- `get_track(track_id) -> Track`
- `get_tracks(track_ids) -> list[Track]`
- `get_album(album_id) -> Album`
- `get_album_tracks(album_id) -> TracksPagingObject`

#### Artists
- `get_artist(artist_id) -> Artist`
- `get_artist_albums(artist_id) -> list[Album]`
- `get_artist_top_tracks(artist_id) -> list[Track]`

#### Playlists
- `get_playlist(playlist_id) -> Playlist`
- `get_playlist_tracks(playlist_id) -> TracksPagingObject`
- `get_playlist_with_tracks(playlist_id) -> PlaylistWithTracks`
- `create_playlist(user_id, name) -> Playlist`
- `add_tracks_to_playlist(playlist_id, track_uris) -> str`
- `remove_tracks_from_playlist(playlist_id, track_uris) -> str`

#### Audio features
- `get_audio_features(track_id) -> AudioFeatures`
- `get_audio_features_multiple(track_ids) -> list[AudioFeatures]`

#### Search & recommendations
- `search(query, type) -> SearchResult`
- `get_recommendations(seed_artists, seed_tracks) -> list[Track]`

## Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest test/test_models.py -v

# Run with coverage
uv run pytest --cov=app
```

### Test Coverage

The project includes comprehensive tests for:

- **Authentication Flow**: PKCE parameter generation, token exchange, refresh
- **Configuration Management**: Environment variable handling, validation
- **Pydantic Models**: All Spotify API object models with validation
- **Type-Safe Client**: All client methods with proper return types
- **Integration Tests**: Full authentication and API interaction flows

## Development

### Code Quality

The project uses modern Python tooling:

- **Ruff**: Fast Python linter and formatter
- **Pytest**: Testing framework
- **Pydantic**: Data validation and serialization
- **Type Hints**: Full type annotation support

Run code quality checks:

```bash
# Lint and format code
uv run ruff check . --fix

# Run tests
uv run pytest

# Check types (if mypy is installed)
uv run mypy app/
```

### Project Structure

```
spotify-exporter/
├── app/
│   ├── __init__.py
│   ├── spotify_auth.py      # PKCE authentication
│   ├── spotify_client.py    # Type-safe API client
│   ├── config.py           # Configuration management
│   ├── models.py           # Pydantic models
│   └── example.py          # Usage examples
├── test/
│   ├── __init__.py
│   ├── test_spotify_auth.py # Authentication tests
│   ├── test_config.py      # Configuration tests
│   └── test_models.py      # Model tests
├── main.py                 # CLI interface
├── pyproject.toml          # Project configuration
├── .env                    # Environment variables
└── README.md              # Documentation
```

## API Reference

### SpotifyAuthManager

High-level authentication manager for the complete PKCE flow.

```python
class SpotifyAuthManager:
    def __init__(self, client_id: str, redirect_uri: str, scope: str | None = None)
    def start_auth_flow(self) -> str
    def complete_auth_flow(self, redirect_url: str) -> spotipy.Spotify
    def refresh_auth(self) -> spotipy.Spotify
    def get_spotify_client(self) -> spotipy.Spotify | None
    def is_authenticated(self) -> bool
```

### SpotifyClient

Type-safe wrapper around the spotipy client with Pydantic models.

```python
class SpotifyClient:
    def __init__(self, spotify_client: spotipy.Spotify)
    # User methods
    def get_current_user(self) -> UserProfile
    def get_user_top_tracks(self, limit: int = 20, time_range: str = 'medium_term') -> list[Track]
    def get_user_top_artists(self, limit: int = 20, time_range: str = 'medium_term') -> list[Artist]
    def get_user_playlists(self, user_id: str, limit: int = 20) -> list[Playlist]
    
    # Track & Album methods
    def get_track(self, track_id: str) -> Track
    def get_tracks(self, track_ids: list[str]) -> list[Track]
    def get_album(self, album_id: str) -> Album
    def get_album_tracks(self, album_id: str, limit: int = 20) -> TracksPagingObject
    
    # Artist methods
    def get_artist(self, artist_id: str) -> Artist
    def get_artist_albums(self, artist_id: str, album_type: str | None = None) -> list[Album]
    def get_artist_top_tracks(self, artist_id: str, country: str = 'US') -> list[Track]
    
    # Playlist methods
    def get_playlist(self, playlist_id: str) -> Playlist
    def get_playlist_tracks(self, playlist_id: str, limit: int = 100) -> TracksPagingObject
    def get_playlist_with_tracks(self, playlist_id: str) -> PlaylistWithTracks
    def create_playlist(self, user_id: str, name: str, description: str = "") -> Playlist
    def add_tracks_to_playlist(self, playlist_id: str, track_uris: list[str]) -> str
    def remove_tracks_from_playlist(self, playlist_id: str, track_uris: list[str]) -> str
    
    # Audio features
    def get_audio_features(self, track_id: str) -> AudioFeatures
    def get_audio_features_multiple(self, track_ids: list[str]) -> list[AudioFeatures]
    
    # Search & recommendations
    def search(self, q: str, type: str = 'track', limit: int = 20) -> SearchResult
    def get_recommendations(self, seed_artists: list[str] | None = None, 
                          seed_tracks: list[str] | None = None, limit: int = 20) -> list[Track]
```

## Spotify Scopes

The following scopes are commonly used:

- `user-read-private`: Read access to user's private information
- `user-read-email`: Read access to user's email address
- `user-top-read`: Read access to user's top artists and tracks
- `playlist-read-private`: Read access to user's private playlists
- `playlist-read-collaborative`: Read access to user's collaborative playlists
- `playlist-modify-public`: Write access to user's public playlists
- `playlist-modify-private`: Write access to user's private playlists
- `user-follow-read`: Read access to user's followed artists
- `user-follow-modify`: Write access to user's followed artists

## Security

- **PKCE Flow**: Uses Proof Key for Code Exchange for secure authentication
- **No Client Secret**: Eliminates the need to store sensitive client secrets
- **State Parameter**: CSRF protection with state parameter validation
- **Environment Variables**: Secure configuration management
- **Token Management**: Automatic token refresh and secure storage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/) for the comprehensive API
- [spotipy](https://spotipy.readthedocs.io/) for the Python Spotify library
- [Pydantic](https://pydantic.dev/) for data validation and serialization
- [PKCE](https://tools.ietf.org/html/rfc7636) for secure OAuth 2.0 flow
