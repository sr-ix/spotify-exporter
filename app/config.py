"""
Configuration module for Spotify API settings.

This module handles environment variables and configuration settings
for the Spotify authentication system.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class SpotifyConfig:
    """Configuration class for Spotify API settings."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.client_id = self._get_required_env("SPOTIFY_CLIENT_ID")
        self.redirect_uri = self._get_required_env("SPOTIFY_REDIRECT_URI")
        self.scope = self._get_optional_env("SPOTIFY_SCOPE", "user-read-private user-read-email")

    def _get_required_env(self, key: str) -> str:
        """
        Get a required environment variable.

        Args:
            key: Environment variable name

        Returns:
            Environment variable value (can be empty)
        """
        return os.getenv(key, "")

    def _get_optional_env(self, key: str, default: str) -> str:
        """
        Get an optional environment variable with a default value.

        Args:
            key: Environment variable name
            default: Default value if environment variable is not set

        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)

    def validate(self) -> bool:
        """
        Validate the configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.client_id:
            raise ValueError("SPOTIFY_CLIENT_ID is required")

        if not self.redirect_uri:
            raise ValueError("SPOTIFY_REDIRECT_URI is required")

        # Basic URL validation
        if not self.redirect_uri.startswith(("http://", "https://")):
            raise ValueError("SPOTIFY_REDIRECT_URI must be a valid URL")

        return True

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scope
        }


def load_config() -> SpotifyConfig:
    """
    Load Spotify configuration from environment variables.

    Returns:
        SpotifyConfig instance

    Raises:
        ValueError: If required configuration is missing
    """
    config = SpotifyConfig()
    config.validate()
    return config


def create_env_template() -> str:
    """
    Create a template for environment variables.

    Returns:
        Environment variables template as a string
    """
    return """# Spotify API Configuration
# Get these values from https://developer.spotify.com/dashboard

# Required: Your Spotify application client ID
SPOTIFY_CLIENT_ID=your_client_id_here

# Required: Redirect URI registered with your Spotify app
# For local development, you can use: http://localhost:8080/callback
SPOTIFY_REDIRECT_URI=http://localhost:8080/callback

# Optional: Spotify API scopes (space-separated)
# Default: user-read-private user-read-email
# Common scopes:
# - user-read-private: Read access to user's private information
# - user-read-email: Read access to user's email address
# - user-top-read: Read access to user's top artists and tracks
# - playlist-read-private: Read access to user's private playlists
# - playlist-read-collaborative: Read access to user's collaborative playlists
SPOTIFY_SCOPE=user-read-private user-read-email user-top-read
"""
