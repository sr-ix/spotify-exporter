# Spotify Exporter

A Python application that authenticates with the Spotify Web API using PKCE (Proof Key for Code Exchange) via the `spotipy` library. This provides a secure way to authenticate with Spotify without requiring a client secret.

## Features

- 🔐 **PKCE Authentication**: Secure OAuth 2.0 flow using PKCE (Proof Key for Code Exchange)
- 🛡️ **No Client Secret Required**: Uses PKCE flow which is recommended for public clients
- 🧪 **Comprehensive Testing**: Full test suite covering all authentication flows
- ⚙️ **Easy Configuration**: Simple environment-based configuration
- 🚀 **CLI Interface**: Command-line interface for easy authentication
- 📦 **Modern Python**: Built with Python 3.13+ and modern tooling

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd spotify-exporter
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   ```bash
   python main.py setup
   ```

4. **Edit the `.env` file** with your Spotify credentials:
   ```bash
   # Get these from https://developer.spotify.com/dashboard
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_REDIRECT_URI=http://localhost:8080/callback
   SPOTIFY_SCOPE=user-read-private user-read-email user-top-read
   ```

## Getting Spotify Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Add `http://localhost:8080/callback` to the Redirect URIs
4. Copy your Client ID to the `.env` file

## Usage

### Command Line Interface

**Set up environment file**:
```bash
python main.py setup
```

**Authenticate with Spotify**:
```bash
python main.py auth
```

This will:
1. Generate an authorization URL
2. Open your browser to authorize the application
3. Complete the authentication flow
4. Test the authenticated client

### Programmatic Usage

```python
from app.spotify_auth import SpotifyAuthManager
from app.config import load_config

# Load configuration
config = load_config()

# Initialize auth manager
auth_manager = SpotifyAuthManager(
    config.client_id,
    config.redirect_uri,
    config.scope
)

# Start authentication flow
auth_url = auth_manager.start_auth_flow()
print(f"Visit this URL: {auth_url}")

# After user authorizes, complete the flow
redirect_url = "http://localhost:8080/callback?code=...&state=..."
spotify_client = auth_manager.complete_auth_flow(redirect_url)

# Use the authenticated client
user = spotify_client.current_user()
print(f"Authenticated as: {user['display_name']}")
```

### Advanced Usage

```python
from app.spotify_auth import SpotifyPKCEAuth

# Direct PKCE authentication
auth = SpotifyPKCEAuth(
    client_id="your_client_id",
    redirect_uri="http://localhost:8080/callback",
    scope="user-read-private user-read-email"
)

# Generate authorization URL
auth_url = auth.get_authorization_url()

# Exchange code for tokens
token_info = auth.exchange_code_for_tokens("authorization_code")

# Create Spotify client
spotify_client = auth.create_spotify_client(token_info["access_token"])

# Refresh tokens when needed
new_token_info = auth.refresh_access_token(token_info["refresh_token"])
```

## Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest test/test_spotify_auth.py

# Run with coverage
uv run pytest --cov=app
```

### Test Coverage

The test suite covers:

- ✅ PKCE parameter generation and validation
- ✅ Authorization URL generation
- ✅ Token exchange and refresh
- ✅ Spotify client creation
- ✅ Error handling and edge cases
- ✅ Configuration management
- ✅ Integration tests

## Development

### Code Quality

Run linting:
```bash
uv run ruff check .
uv run ruff format .
```

### Project Structure

```
spotify-exporter/
├── app/
│   ├── __init__.py
│   ├── spotify_auth.py      # Main authentication module
│   ├── config.py           # Configuration management
│   └── example.py          # Usage examples
├── test/
│   ├── __init__.py
│   ├── test_spotify_auth.py # Authentication tests
│   └── test_config.py      # Configuration tests
├── main.py                 # CLI interface
├── pyproject.toml          # Project configuration
└── README.md              # This file
```

## API Reference

### SpotifyPKCEAuth

Main authentication handler class.

**Methods**:
- `generate_pkce_params()`: Generate PKCE code verifier and challenge
- `get_authorization_url()`: Generate Spotify authorization URL
- `exchange_code_for_tokens(code)`: Exchange authorization code for tokens
- `refresh_access_token(refresh_token)`: Refresh expired access token
- `create_spotify_client(access_token)`: Create authenticated Spotify client
- `validate_authorization_response(url)`: Validate redirect URL

### SpotifyAuthManager

High-level authentication manager.

**Methods**:
- `start_auth_flow()`: Start authentication and return authorization URL
- `complete_auth_flow(redirect_url)`: Complete authentication with redirect URL
- `refresh_auth()`: Refresh authentication tokens
- `get_spotify_client()`: Get current Spotify client
- `is_authenticated()`: Check authentication status

### SpotifyConfig

Configuration management class.

**Methods**:
- `validate()`: Validate configuration
- `to_dict()`: Convert to dictionary

## Spotify Scopes

Common scopes you can use:

- `user-read-private`: Read access to user's private information
- `user-read-email`: Read access to user's email address
- `user-top-read`: Read access to user's top artists and tracks
- `playlist-read-private`: Read access to user's private playlists
- `playlist-read-collaborative`: Read access to user's collaborative playlists
- `user-library-read`: Read access to user's library
- `user-follow-read`: Read access to user's followed artists and playlists

## Security

- Uses PKCE (Proof Key for Code Exchange) for secure authentication
- No client secret required or stored
- State parameter for CSRF protection
- Secure token handling
- Environment variable configuration

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

- [Spotipy](https://spotipy.readthedocs.io/) - Spotify Web API wrapper
- [PKCE](https://github.com/spotipy-dev/pkce) - PKCE implementation
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/) - Official API documentation
