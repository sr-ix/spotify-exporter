"""
Tests for the Spotify PKCE authentication system.

This module contains comprehensive tests for the SpotifyAuthManager and
SpotifyPKCEAuth classes, covering all authentication flows and edge cases.
"""

from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

import pytest

from app.spotify_auth import SpotifyAuthManager, SpotifyPKCEAuth


class TestSpotifyPKCEAuth:
    """Test cases for the SpotifyPKCEAuth class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client_id = "test_client_id"
        self.redirect_uri = "http://localhost:8080/callback"
        self.scope = "user-read-private user-read-email"
        self.auth = SpotifyPKCEAuth(self.client_id, self.redirect_uri, self.scope)

    def test_init(self):
        """Test initialization of SpotifyPKCEAuth."""
        assert self.auth.client_id == self.client_id
        assert self.auth.redirect_uri == self.redirect_uri
        assert self.auth.scope == self.scope
        assert self.auth.state is not None
        assert len(self.auth.state) > 0
        assert self.auth.code_verifier is None
        assert self.auth.code_challenge is None
        assert self.auth.oauth is None

    def test_init_with_custom_state(self):
        """Test initialization with custom state parameter."""
        custom_state = "custom_state_value"
        auth = SpotifyPKCEAuth(self.client_id, self.redirect_uri, self.scope, custom_state)
        assert auth.state == custom_state

    def test_init_with_default_scope(self):
        """Test initialization with default scope."""
        auth = SpotifyPKCEAuth(self.client_id, self.redirect_uri)
        assert auth.scope == "user-read-private user-read-email"

    def test_generate_pkce_params(self):
        """Test PKCE parameter generation."""
        params = self.auth.generate_pkce_params()

        assert "code_verifier" in params
        assert "code_challenge" in params
        assert self.auth.code_verifier == params["code_verifier"]
        assert self.auth.code_challenge == params["code_challenge"]
        assert len(self.auth.code_verifier) == 128
        assert len(self.auth.code_challenge) > 0

    def test_get_authorization_url(self):
        """Test authorization URL generation."""
        auth_url = self.auth.get_authorization_url()

        # Parse the URL
        parsed = urlparse(auth_url)
        params = parse_qs(parsed.query)

        # Check base URL
        assert parsed.scheme == "https"
        assert parsed.netloc == "accounts.spotify.com"
        assert parsed.path == "/authorize"

        # Check required parameters
        assert params["client_id"][0] == self.client_id
        assert params["response_type"][0] == "code"
        assert params["redirect_uri"][0] == self.redirect_uri
        assert params["scope"][0] == self.scope
        assert params["state"][0] == self.auth.state
        assert params["code_challenge_method"][0] == "S256"
        assert "code_challenge" in params

        # Verify PKCE parameters were generated
        assert self.auth.code_verifier is not None
        assert self.auth.code_challenge is not None

    def test_get_authorization_url_auto_generates_pkce(self):
        """Test that authorization URL auto-generates PKCE parameters."""
        # Ensure no PKCE parameters exist initially
        self.auth.code_verifier = None
        self.auth.code_challenge = None

        auth_url = self.auth.get_authorization_url()

        # Verify PKCE parameters were auto-generated
        assert self.auth.code_verifier is not None
        assert self.auth.code_challenge is not None

        # Verify URL contains the challenge
        parsed = urlparse(auth_url)
        params = parse_qs(parsed.query)
        assert params["code_challenge"][0] == self.auth.code_challenge

    @patch('app.spotify_auth.SpotifyOAuth')
    def test_exchange_code_for_tokens_success(self, mock_spotify_oauth):
        """Test successful token exchange."""
        # Setup mock
        mock_oauth_instance = Mock()
        mock_spotify_oauth.return_value = mock_oauth_instance

        expected_token_info = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        mock_oauth_instance.get_access_token.return_value = expected_token_info

        # Generate PKCE parameters first
        self.auth.generate_pkce_params()

        # Test token exchange
        result = self.auth.exchange_code_for_tokens("test_auth_code")

        # Verify result
        assert result == expected_token_info

        # Verify SpotifyOAuth was called correctly
        mock_spotify_oauth.assert_called_once_with(
            client_id=self.client_id,
            client_secret=None,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            state=self.auth.state,
            open_browser=False,
            cache_handler=None
        )

        mock_oauth_instance.get_access_token.assert_called_once_with(
            code="test_auth_code",
            as_dict=True
        )

    def test_exchange_code_for_tokens_no_verifier(self):
        """Test token exchange without code verifier."""
        with pytest.raises(ValueError, match="Code verifier not set"):
            self.auth.exchange_code_for_tokens("test_auth_code")

    @patch('app.spotify_auth.SpotifyOAuth')
    def test_refresh_access_token(self, mock_spotify_oauth):
        """Test access token refresh."""
        # Setup mock
        mock_oauth_instance = Mock()
        mock_spotify_oauth.return_value = mock_oauth_instance

        expected_token_info = {
            "access_token": "new_access_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        mock_oauth_instance.refresh_access_token.return_value = expected_token_info

        # Test token refresh
        result = self.auth.refresh_access_token("test_refresh_token")

        # Verify result
        assert result == expected_token_info

        # Verify SpotifyOAuth was called correctly
        mock_spotify_oauth.assert_called_once_with(
            client_id=self.client_id,
            client_secret=None,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            state=self.auth.state,
            open_browser=False,
            cache_handler=None
        )

        mock_oauth_instance.refresh_access_token.assert_called_once_with("test_refresh_token")

    @patch('app.spotify_auth.spotipy.Spotify')
    def test_create_spotify_client(self, mock_spotify):
        """Test Spotify client creation."""
        mock_client = Mock()
        mock_spotify.return_value = mock_client

        result = self.auth.create_spotify_client("test_access_token")

        assert result == mock_client
        mock_spotify.assert_called_once_with(auth="test_access_token")

    def test_validate_authorization_response_success(self):
        """Test successful authorization response validation."""
        auth_code = "test_auth_code"
        redirect_url = f"http://localhost:8080/callback?code={auth_code}&state={self.auth.state}"

        result = self.auth.validate_authorization_response(redirect_url)

        assert result == auth_code

    def test_validate_authorization_response_no_code(self):
        """Test authorization response without code."""
        redirect_url = f"http://localhost:8080/callback?state={self.auth.state}"

        result = self.auth.validate_authorization_response(redirect_url)

        assert result is None

    def test_validate_authorization_response_invalid_state(self):
        """Test authorization response with invalid state."""
        redirect_url = "http://localhost:8080/callback?code=test_code&state=invalid_state"

        with pytest.raises(ValueError, match="Invalid state parameter"):
            self.auth.validate_authorization_response(redirect_url)

    def test_validate_authorization_response_error(self):
        """Test authorization response with error."""
        redirect_url = "http://localhost:8080/callback?error=access_denied&state=test_state"

        with pytest.raises(ValueError, match="Authorization error: access_denied"):
            self.auth.validate_authorization_response(redirect_url)


class TestSpotifyAuthManager:
    """Test cases for the SpotifyAuthManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client_id = "test_client_id"
        self.redirect_uri = "http://localhost:8080/callback"
        self.scope = "user-read-private user-read-email"
        self.auth_manager = SpotifyAuthManager(self.client_id, self.redirect_uri, self.scope)

    def test_init(self):
        """Test initialization of SpotifyAuthManager."""
        assert self.auth_manager.auth_handler.client_id == self.client_id
        assert self.auth_manager.auth_handler.redirect_uri == self.redirect_uri
        assert self.auth_manager.auth_handler.scope == self.scope
        assert self.auth_manager.access_token is None
        assert self.auth_manager.refresh_token is None
        assert self.auth_manager.spotify_client is None

    def test_start_auth_flow(self):
        """Test starting the authentication flow."""
        auth_url = self.auth_manager.start_auth_flow()

        # Verify URL is generated
        assert auth_url.startswith("https://accounts.spotify.com/authorize")

        # Verify PKCE parameters were generated
        assert self.auth_manager.auth_handler.code_verifier is not None
        assert self.auth_manager.auth_handler.code_challenge is not None

    @patch('app.spotify_auth.spotipy.Spotify')
    def test_complete_auth_flow_success(self, mock_spotify):
        """Test successful authentication flow completion."""
        # Setup mocks
        mock_client = Mock()
        mock_spotify.return_value = mock_client

        # Mock the auth handler methods
        self.auth_manager.auth_handler.validate_authorization_response = Mock(
            return_value="test_auth_code"
        )
        self.auth_manager.auth_handler.exchange_code_for_tokens = Mock(
            return_value={
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "expires_in": 3600
            }
        )
        self.auth_manager.auth_handler.create_spotify_client = Mock(
            return_value=mock_client
        )

        # Test completion
        result = self.auth_manager.complete_auth_flow("test_redirect_url")

        # Verify result
        assert result == mock_client

        # Verify tokens were stored
        assert self.auth_manager.access_token == "test_access_token"
        assert self.auth_manager.refresh_token == "test_refresh_token"
        assert self.auth_manager.spotify_client == mock_client

        # Verify methods were called
        self.auth_manager.auth_handler.validate_authorization_response.assert_called_once_with("test_redirect_url")
        self.auth_manager.auth_handler.exchange_code_for_tokens.assert_called_once_with("test_auth_code")
        self.auth_manager.auth_handler.create_spotify_client.assert_called_once_with("test_access_token")

    def test_complete_auth_flow_no_code(self):
        """Test authentication flow completion with no authorization code."""
        # Mock the auth handler to return None for code
        self.auth_manager.auth_handler.validate_authorization_response = Mock(return_value=None)

        with pytest.raises(ValueError, match="No authorization code found in redirect URL"):
            self.auth_manager.complete_auth_flow("test_redirect_url")

    @patch('app.spotify_auth.spotipy.Spotify')
    def test_refresh_auth_success(self, mock_spotify):
        """Test successful token refresh."""
        # Setup initial state
        self.auth_manager.refresh_token = "test_refresh_token"
        mock_client = Mock()
        mock_spotify.return_value = mock_client

        # Mock the auth handler methods
        self.auth_manager.auth_handler.refresh_access_token = Mock(
            return_value={
                "access_token": "new_access_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 3600
            }
        )
        self.auth_manager.auth_handler.create_spotify_client = Mock(
            return_value=mock_client
        )

        # Test refresh
        result = self.auth_manager.refresh_auth()

        # Verify result
        assert result == mock_client

        # Verify tokens were updated
        assert self.auth_manager.access_token == "new_access_token"
        assert self.auth_manager.refresh_token == "new_refresh_token"
        assert self.auth_manager.spotify_client == mock_client

        # Verify methods were called
        self.auth_manager.auth_handler.refresh_access_token.assert_called_once_with("test_refresh_token")
        self.auth_manager.auth_handler.create_spotify_client.assert_called_once_with("new_access_token")

    def test_refresh_auth_no_refresh_token(self):
        """Test token refresh without refresh token."""
        self.auth_manager.refresh_token = None

        with pytest.raises(ValueError, match="No refresh token available"):
            self.auth_manager.refresh_auth()

    def test_get_spotify_client_authenticated(self):
        """Test getting Spotify client when authenticated."""
        mock_client = Mock()
        self.auth_manager.spotify_client = mock_client

        result = self.auth_manager.get_spotify_client()

        assert result == mock_client

    def test_get_spotify_client_not_authenticated(self):
        """Test getting Spotify client when not authenticated."""
        result = self.auth_manager.get_spotify_client()

        assert result is None

    def test_is_authenticated_true(self):
        """Test authentication status when authenticated."""
        self.auth_manager.spotify_client = Mock()
        self.auth_manager.access_token = "test_token"

        assert self.auth_manager.is_authenticated() is True

    def test_is_authenticated_false_no_client(self):
        """Test authentication status when no client."""
        self.auth_manager.spotify_client = None
        self.auth_manager.access_token = "test_token"

        assert self.auth_manager.is_authenticated() is False

    def test_is_authenticated_false_no_token(self):
        """Test authentication status when no token."""
        self.auth_manager.spotify_client = Mock()
        self.auth_manager.access_token = None

        assert self.auth_manager.is_authenticated() is False

    def test_is_authenticated_false_neither(self):
        """Test authentication status when neither client nor token."""
        self.auth_manager.spotify_client = None
        self.auth_manager.access_token = None

        assert self.auth_manager.is_authenticated() is False


class TestIntegration:
    """Integration tests for the authentication system."""

    def test_full_auth_flow_integration(self):
        """Test the complete authentication flow integration."""
        client_id = "test_client_id"
        redirect_uri = "http://localhost:8080/callback"
        scope = "user-read-private"

        # Create auth manager
        auth_manager = SpotifyAuthManager(client_id, redirect_uri, scope)

        # Start auth flow
        auth_url = auth_manager.start_auth_flow()

        # Verify auth URL is properly formatted
        assert "accounts.spotify.com" in auth_url
        assert "client_id=" in auth_url
        assert "code_challenge=" in auth_url
        assert "state=" in auth_url

        # Verify PKCE parameters were generated
        assert auth_manager.auth_handler.code_verifier is not None
        assert auth_manager.auth_handler.code_challenge is not None

        # Verify not authenticated initially
        assert not auth_manager.is_authenticated()
        assert auth_manager.get_spotify_client() is None

    def test_pkce_parameter_consistency(self):
        """Test that PKCE parameters are consistent across multiple calls."""
        auth = SpotifyPKCEAuth("test_id", "http://localhost/callback")

        # Generate parameters
        auth.generate_pkce_params()
        verifier1 = auth.code_verifier
        challenge1 = auth.code_challenge

        # Generate again
        auth.generate_pkce_params()
        verifier2 = auth.code_verifier
        challenge2 = auth.code_challenge

        # Parameters should be different (random)
        assert verifier1 != verifier2
        assert challenge1 != challenge2

        # But each pair should be consistent
        assert len(verifier1) == len(verifier2) == 128
        assert len(challenge1) == len(challenge2) > 0
