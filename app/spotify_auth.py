"""
Spotify Authentication Module using PKCE (Proof Key for Code Exchange).

This module provides a secure way to authenticate with the Spotify Web API
using the PKCE flow, which is recommended for public clients.
"""

import secrets
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import spotipy
from pkce import generate_code_verifier, get_code_challenge
from spotipy.oauth2 import SpotifyOAuth


class SpotifyPKCEAuth:
    """
    Spotify authentication handler using PKCE flow.

    This class manages the OAuth 2.0 PKCE flow for authenticating with Spotify.
    It handles code verifier generation, authorization URL creation, and token exchange.
    """

    def __init__(
        self,
        client_id: str,
        redirect_uri: str,
        scope: str | None = None,
        state: str | None = None
    ):
        """
        Initialize the Spotify PKCE authentication handler.

        Args:
            client_id: Spotify application client ID
            redirect_uri: Redirect URI registered with Spotify app
            scope: Space-separated list of Spotify scopes
            state: Optional state parameter for CSRF protection
        """
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scope = scope or "user-read-private user-read-email"
        self.state = state or secrets.token_urlsafe(32)

        # PKCE parameters
        self.code_verifier = None
        self.code_challenge = None

        # Spotify OAuth instance
        self.oauth = None

    def generate_pkce_params(self) -> dict[str, str]:
        """
        Generate PKCE code verifier and challenge.

        Returns:
            Dictionary containing code_verifier and code_challenge
        """
        self.code_verifier = generate_code_verifier(length=128)
        self.code_challenge = get_code_challenge(self.code_verifier)

        return {
            "code_verifier": self.code_verifier,
            "code_challenge": self.code_challenge
        }

    def get_authorization_url(self) -> str:
        """
        Generate the authorization URL for Spotify OAuth.

        Returns:
            Authorization URL that the user should visit
        """
        if not self.code_challenge:
            self.generate_pkce_params()

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scope,
            "state": self.state,
            "code_challenge_method": "S256",
            "code_challenge": self.code_challenge
        }

        auth_url = "https://accounts.spotify.com/authorize"
        return f"{auth_url}?{urlencode(params)}"

    def exchange_code_for_tokens(self, authorization_code: str) -> dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.

        Args:
            authorization_code: Authorization code received from Spotify

        Returns:
            Dictionary containing access_token, refresh_token, and other token info

        Raises:
            ValueError: If code_verifier is not set
            Exception: If token exchange fails
        """
        if not self.code_verifier:
            raise ValueError("Code verifier not set. Call get_authorization_url() first.")

        # Create SpotifyOAuth instance for token exchange
        self.oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=None,  # Not needed for PKCE
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            state=self.state,
            open_browser=False,
            cache_handler=None
        )

        # Exchange code for tokens
        token_info = self.oauth.get_access_token(
            code=authorization_code,
            as_dict=True
        )

        return token_info

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """
        Refresh an expired access token using the refresh token.

        Args:
            refresh_token: Refresh token from previous authentication

        Returns:
            Dictionary containing new access_token and other token info
        """
        if not self.oauth:
            self.oauth = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=None,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                state=self.state,
                open_browser=False,
                cache_handler=None
            )

        token_info = self.oauth.refresh_access_token(refresh_token)
        return token_info

    def create_spotify_client(self, access_token: str) -> spotipy.Spotify:
        """
        Create a Spotify client instance with the provided access token.

        Args:
            access_token: Valid access token

        Returns:
            Authenticated Spotify client instance
        """
        return spotipy.Spotify(auth=access_token)

    def validate_authorization_response(self, url: str) -> str | None:
        """
        Validate and extract authorization code from redirect URL.

        Args:
            url: Redirect URL received from Spotify

        Returns:
            Authorization code if valid, None otherwise

        Raises:
            ValueError: If URL is invalid or contains error
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Check for errors
        if "error" in query_params:
            error = query_params["error"][0]
            raise ValueError(f"Authorization error: {error}")

        # Validate state parameter
        if "state" not in query_params or query_params["state"][0] != self.state:
            raise ValueError("Invalid state parameter")

        # Extract authorization code
        if "code" not in query_params:
            return None

        return query_params["code"][0]


class SpotifyAuthManager:
    """
    High-level manager for Spotify authentication flow.

    This class provides a simplified interface for the complete authentication process.
    """

    def __init__(
        self,
        client_id: str,
        redirect_uri: str,
        scope: str | None = None
    ):
        """
        Initialize the Spotify authentication manager.

        Args:
            client_id: Spotify application client ID
            redirect_uri: Redirect URI registered with Spotify app
            scope: Space-separated list of Spotify scopes
        """
        self.auth_handler = SpotifyPKCEAuth(client_id, redirect_uri, scope)
        self.access_token = None
        self.refresh_token = None
        self.spotify_client = None

    def start_auth_flow(self) -> str:
        """
        Start the authentication flow and return the authorization URL.

        Returns:
            Authorization URL for the user to visit
        """
        return self.auth_handler.get_authorization_url()

    def complete_auth_flow(self, redirect_url: str) -> spotipy.Spotify:
        """
        Complete the authentication flow using the redirect URL.

        Args:
            redirect_url: Redirect URL received from Spotify

        Returns:
            Authenticated Spotify client instance

        Raises:
            ValueError: If authentication fails
        """
        # Extract authorization code
        auth_code = self.auth_handler.validate_authorization_response(redirect_url)
        if not auth_code:
            raise ValueError("No authorization code found in redirect URL")

        # Exchange code for tokens
        token_info = self.auth_handler.exchange_code_for_tokens(auth_code)

        # Store tokens
        self.access_token = token_info["access_token"]
        self.refresh_token = token_info.get("refresh_token")

        # Create Spotify client
        self.spotify_client = self.auth_handler.create_spotify_client(self.access_token)

        return self.spotify_client

    def refresh_auth(self) -> spotipy.Spotify:
        """
        Refresh the access token using the stored refresh token.

        Returns:
            Updated Spotify client instance

        Raises:
            ValueError: If no refresh token is available
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")

        # Refresh tokens
        token_info = self.auth_handler.refresh_access_token(self.refresh_token)

        # Update stored tokens
        self.access_token = token_info["access_token"]
        if "refresh_token" in token_info:
            self.refresh_token = token_info["refresh_token"]

        # Update Spotify client
        self.spotify_client = self.auth_handler.create_spotify_client(self.access_token)

        return self.spotify_client

    def get_spotify_client(self) -> spotipy.Spotify | None:
        """
        Get the current Spotify client instance.

        Returns:
            Spotify client instance if authenticated, None otherwise
        """
        return self.spotify_client

    def is_authenticated(self) -> bool:
        """
        Check if the client is currently authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self.spotify_client is not None and self.access_token is not None
