"""
Spotify Exporter - Main CLI Interface

This module provides a command-line interface for the Spotify authentication system.
"""

import argparse
import sys
from pathlib import Path

from app.config import create_env_template, load_config
from app.spotify_auth import SpotifyAuthManager


def setup_env_file():
    """Create a .env file template if it doesn't exist."""
    env_file = Path(".env")
    if not env_file.exists():
        template = create_env_template()
        env_file.write_text(template)
        print("Created .env file template. Please edit it with your Spotify credentials.")
        print("You can get your credentials from: https://developer.spotify.com/dashboard")
        return False
    return True


def authenticate():
    """Run the authentication flow."""
    try:
        # Load configuration
        config = load_config()
        print("✅ Configuration loaded successfully")
        print(f"   Client ID: {config.client_id}")
        print(f"   Redirect URI: {config.redirect_uri}")
        print(f"   Scope: {config.scope}")
        print()

        # Initialize auth manager
        auth_manager = SpotifyAuthManager(
            config.client_id,
            config.redirect_uri,
            config.scope
        )

        # Start authentication flow
        print("🔐 Starting Spotify authentication...")
        auth_url = auth_manager.start_auth_flow()
        print(f"📋 Authorization URL: {auth_url}")
        print()
        print("Please visit the above URL in your browser to authorize the application.")
        print("After authorization, you'll be redirected to a URL. Copy that URL and paste it below.")
        print()

        # Get redirect URL from user
        redirect_url = input("Enter the redirect URL: ").strip()

        if not redirect_url:
            print("❌ No redirect URL provided. Exiting.")
            return 1

        # Complete authentication
        print("🔄 Completing authentication...")
        spotify_client = auth_manager.complete_auth_flow(redirect_url)
        print("✅ Authentication successful!")
        print()

        # Test the authenticated client
        print("🧪 Testing authenticated client...")
        user = spotify_client.current_user()
        print(f"✅ Authenticated as: {user['display_name']} ({user['email']})")
        print()

        # Show available scopes
        print("📋 Available scopes:")
        for scope in config.scope.split():
            print(f"   - {scope}")
        print()

        print("🎉 Authentication complete! You can now use the Spotify API.")
        return 0

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Spotify Exporter - Authenticate with Spotify API using PKCE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py auth          # Run authentication flow
  python main.py setup         # Create .env file template
        """
    )

    parser.add_argument(
        "command",
        choices=["auth", "setup"],
        help="Command to run"
    )

    args = parser.parse_args()

    if args.command == "setup":
        if setup_env_file():
            print("✅ .env file already exists")
        return 0

    elif args.command == "auth":
        if not setup_env_file():
            print("Please configure your .env file and run 'python main.py auth' again.")
            return 1
        return authenticate()


if __name__ == "__main__":
    sys.exit(main())
