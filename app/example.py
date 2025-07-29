"""
Example usage of the Spotify PKCE authentication system.

This script demonstrates how to use the SpotifyAuthManager to authenticate
with Spotify using the PKCE flow.
"""

import os

from app.spotify_auth import SpotifyAuthManager


def main():
    """
    Example authentication flow.

    This function demonstrates the complete authentication process:
    1. Initialize the auth manager
    2. Start the auth flow and get authorization URL
    3. Complete the auth flow with the redirect URL
    4. Use the authenticated Spotify client
    """
    # Configuration - these would typically come from environment variables
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "your_client_id_here")
    REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8080/callback")
    SCOPE = "user-read-private user-read-email user-top-read"

    # Initialize the authentication manager
    auth_manager = SpotifyAuthManager(CLIENT_ID, REDIRECT_URI, SCOPE)

    print("=== Spotify PKCE Authentication Example ===")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Redirect URI: {REDIRECT_URI}")
    print(f"Scope: {SCOPE}")
    print()

    # Step 1: Start the authentication flow
    print("1. Starting authentication flow...")
    auth_url = auth_manager.start_auth_flow()
    print(f"Authorization URL: {auth_url}")
    print()
    print("Please visit the above URL in your browser to authorize the application.")
    print("After authorization, you'll be redirected to a URL. Copy that URL and paste it below.")
    print()

    # Step 2: Get the redirect URL from user
    redirect_url = input("Enter the redirect URL: ").strip()

    try:
        # Step 3: Complete the authentication flow
        print("2. Completing authentication flow...")
        spotify_client = auth_manager.complete_auth_flow(redirect_url)
        print("✅ Authentication successful!")
        print()

        # Step 4: Use the authenticated client
        print("3. Testing authenticated client...")
        user = spotify_client.current_user()
        print(f"✅ Authenticated as: {user['display_name']} ({user['email']})")
        print()

        # Example: Get user's top tracks
        print("4. Fetching user's top tracks...")
        top_tracks = spotify_client.current_user_top_tracks(limit=5, offset=0, time_range='short_term')
        print("Top tracks:")
        for i, track in enumerate(top_tracks['items'], 1):
            print(f"  {i}. {track['name']} - {track['artists'][0]['name']}")
        print()

        # Example: Check if we can refresh tokens
        if auth_manager.refresh_token:
            print("5. Testing token refresh capability...")
            print("✅ Refresh token available - can refresh access token when needed")
        else:
            print("5. Testing token refresh capability...")
            print("⚠️  No refresh token available")

        print()
        print("=== Authentication Example Complete ===")

    except ValueError as e:
        print(f"❌ Authentication failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
