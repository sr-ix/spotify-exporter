"""
Tests for the Spotify configuration module.

This module contains tests for the SpotifyConfig class and related functions.
"""

import os

import pytest

from app.config import SpotifyConfig, create_env_template, load_config


class TestSpotifyConfig:
    """Test cases for the SpotifyConfig class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clear any existing environment variables
        for key in ["SPOTIFY_CLIENT_ID", "SPOTIFY_REDIRECT_URI", "SPOTIFY_SCOPE"]:
            if key in os.environ:
                del os.environ[key]

    def test_init_with_required_env_vars(self):
        """Test initialization with required environment variables."""
        os.environ["SPOTIFY_CLIENT_ID"] = "test_client_id"
        os.environ["SPOTIFY_REDIRECT_URI"] = "http://localhost:8080/callback"

        config = SpotifyConfig()

        assert config.client_id == "test_client_id"
        assert config.redirect_uri == "http://localhost:8080/callback"
        assert config.scope == "user-read-private user-read-email"  # default

    def test_init_with_all_env_vars(self):
        """Test initialization with all environment variables."""
        os.environ["SPOTIFY_CLIENT_ID"] = "test_client_id"
        os.environ["SPOTIFY_REDIRECT_URI"] = "http://localhost:8080/callback"
        os.environ["SPOTIFY_SCOPE"] = "user-read-private user-top-read"

        config = SpotifyConfig()

        assert config.client_id == "test_client_id"
        assert config.redirect_uri == "http://localhost:8080/callback"
        assert config.scope == "user-read-private user-top-read"

    def test_init_missing_client_id(self):
        """Test initialization with missing client ID."""
        os.environ["SPOTIFY_REDIRECT_URI"] = "http://localhost:8080/callback"

        config = SpotifyConfig()
        with pytest.raises(ValueError, match="SPOTIFY_CLIENT_ID is required"):
            config.validate()

    def test_init_missing_redirect_uri(self):
        """Test initialization with missing redirect URI."""
        os.environ["SPOTIFY_CLIENT_ID"] = "test_client_id"

        config = SpotifyConfig()
        with pytest.raises(ValueError, match="SPOTIFY_REDIRECT_URI is required"):
            config.validate()

    def test_validate_success(self):
        """Test successful validation."""
        os.environ["SPOTIFY_CLIENT_ID"] = "test_client_id"
        os.environ["SPOTIFY_REDIRECT_URI"] = "http://localhost:8080/callback"

        config = SpotifyConfig()
        assert config.validate() is True

    def test_validate_empty_client_id(self):
        """Test validation with empty client ID."""
        os.environ["SPOTIFY_CLIENT_ID"] = ""
        os.environ["SPOTIFY_REDIRECT_URI"] = "http://localhost:8080/callback"

        config = SpotifyConfig()
        with pytest.raises(ValueError, match="SPOTIFY_CLIENT_ID is required"):
            config.validate()

    def test_validate_empty_redirect_uri(self):
        """Test validation with empty redirect URI."""
        os.environ["SPOTIFY_CLIENT_ID"] = "test_client_id"
        os.environ["SPOTIFY_REDIRECT_URI"] = ""

        config = SpotifyConfig()
        with pytest.raises(ValueError, match="SPOTIFY_REDIRECT_URI is required"):
            config.validate()

    def test_validate_invalid_redirect_uri(self):
        """Test validation with invalid redirect URI."""
        os.environ["SPOTIFY_CLIENT_ID"] = "test_client_id"
        os.environ["SPOTIFY_REDIRECT_URI"] = "invalid-url"

        config = SpotifyConfig()
        with pytest.raises(ValueError, match="SPOTIFY_REDIRECT_URI must be a valid URL"):
            config.validate()

    def test_validate_https_redirect_uri(self):
        """Test validation with HTTPS redirect URI."""
        os.environ["SPOTIFY_CLIENT_ID"] = "test_client_id"
        os.environ["SPOTIFY_REDIRECT_URI"] = "https://example.com/callback"

        config = SpotifyConfig()
        assert config.validate() is True

    def test_to_dict(self):
        """Test conversion to dictionary."""
        os.environ["SPOTIFY_CLIENT_ID"] = "test_client_id"
        os.environ["SPOTIFY_REDIRECT_URI"] = "http://localhost:8080/callback"
        os.environ["SPOTIFY_SCOPE"] = "user-read-private user-top-read"

        config = SpotifyConfig()
        config_dict = config.to_dict()

        expected = {
            "client_id": "test_client_id",
            "redirect_uri": "http://localhost:8080/callback",
            "scope": "user-read-private user-top-read"
        }

        assert config_dict == expected


class TestLoadConfig:
    """Test cases for the load_config function."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clear any existing environment variables
        for key in ["SPOTIFY_CLIENT_ID", "SPOTIFY_REDIRECT_URI", "SPOTIFY_SCOPE"]:
            if key in os.environ:
                del os.environ[key]

    def test_load_config_success(self):
        """Test successful configuration loading."""
        os.environ["SPOTIFY_CLIENT_ID"] = "test_client_id"
        os.environ["SPOTIFY_REDIRECT_URI"] = "http://localhost:8080/callback"

        config = load_config()

        assert config.client_id == "test_client_id"
        assert config.redirect_uri == "http://localhost:8080/callback"
        assert config.scope == "user-read-private user-read-email"

    def test_load_config_missing_required(self):
        """Test configuration loading with missing required variables."""
        with pytest.raises(ValueError, match="SPOTIFY_CLIENT_ID is required"):
            load_config()

    def test_load_config_invalid_redirect_uri(self):
        """Test configuration loading with invalid redirect URI."""
        os.environ["SPOTIFY_CLIENT_ID"] = "test_client_id"
        os.environ["SPOTIFY_REDIRECT_URI"] = "invalid-url"

        with pytest.raises(ValueError, match="SPOTIFY_REDIRECT_URI must be a valid URL"):
            load_config()


class TestCreateEnvTemplate:
    """Test cases for the create_env_template function."""

    def test_create_env_template(self):
        """Test environment template creation."""
        template = create_env_template()

        # Check that template contains expected content
        assert "SPOTIFY_CLIENT_ID=" in template
        assert "SPOTIFY_REDIRECT_URI=" in template
        assert "SPOTIFY_SCOPE=" in template
        assert "your_client_id_here" in template
        assert "http://localhost:8080/callback" in template
        assert "user-read-private user-read-email user-top-read" in template

        # Check that it contains helpful comments
        assert "# Spotify API Configuration" in template
        assert "# Get these values from https://developer.spotify.com/dashboard" in template
        assert "# Required:" in template
        assert "# Optional:" in template
