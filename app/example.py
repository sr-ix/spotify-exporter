"""
Example usage of the Spotify PKCE authentication system with Pydantic models.

This script demonstrates how to use the SpotifyAuthManager and SpotifyClient
to authenticate with Spotify and work with type-safe Pydantic models.
"""

import os

from app.spotify_auth import SpotifyAuthManager
from app.spotify_client import SpotifyClient


def main():
    """
    Example authentication flow with Pydantic models.

    This function demonstrates the complete authentication process:
    1. Initialize the auth manager
    2. Start the auth flow and get authorization URL
    3. Complete the auth flow with the redirect URL
    4. Use the authenticated Spotify client with Pydantic models
    """
    # Configuration - these would typically come from environment variables
    CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "your_client_id_here")
    REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8080/callback")
    SCOPE = "user-read-private user-read-email user-top-read playlist-read-private"

    # Initialize the authentication manager
    auth_manager = SpotifyAuthManager(CLIENT_ID, REDIRECT_URI, SCOPE)

    print("=== Spotify PKCE Authentication with Pydantic Models ===")
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
        spotify_client_raw = auth_manager.complete_auth_flow(redirect_url)
        print("✅ Authentication successful!")
        print()

        # Step 4: Create type-safe client wrapper
        print("3. Creating type-safe Spotify client...")
        spotify_client = SpotifyClient(spotify_client_raw)
        print("✅ Type-safe client created!")
        print()

        # Step 5: Get user profile with Pydantic model
        print("4. Getting user profile...")
        user = spotify_client.get_current_user()
        print(f"✅ Authenticated as: {user.display_name} ({user.email})")
        print(f"   User ID: {user.id}")
        print(f"   Country: {user.country}")
        print(f"   Product: {user.product}")
        print(f"   Followers: {user.followers.total if user.followers else 0}")
        print()

        # Step 6: Get user's top tracks with Pydantic models
        print("5. Fetching user's top tracks...")
        top_tracks = spotify_client.get_user_top_tracks(limit=5, time_range='short_term')
        print("Top tracks:")
        for i, track in enumerate(top_tracks, 1):
            print(f"  {i}. {track.name} - {track.artists[0].name}")
            print(f"     Album: {track.album.name}")
            print(f"     Duration: {track.duration_ms // 1000}s")
            print(f"     Popularity: {track.popularity}")
            print(f"     Explicit: {track.explicit}")
            print()
        print()

        # Step 7: Get user's top artists
        print("6. Fetching user's top artists...")
        top_artists = spotify_client.get_user_top_artists(limit=3, time_range='short_term')
        print("Top artists:")
        for i, artist in enumerate(top_artists, 1):
            print(f"  {i}. {artist.name}")
            print(f"     Popularity: {artist.popularity}")
            print(f"     Genres: {', '.join(artist.genres) if artist.genres else 'None'}")
            print(f"     Followers: {artist.followers.total if artist.followers else 0}")
            print()
        print()

        # Step 8: Search for tracks
        print("7. Searching for tracks...")
        search_query = input("Enter a search query (or press Enter for 'The Beatles'): ").strip()
        if not search_query:
            search_query = "The Beatles"

        search_results = spotify_client.search(search_query, type='track', limit=3)
        if search_results.tracks and search_results.tracks.items:
            print(f"Search results for '{search_query}':")
            for i, track in enumerate(search_results.tracks.items, 1):
                print(f"  {i}. {track.name} - {track.artists[0].name}")
                print(f"     Album: {track.album.name}")
                print(f"     Release Date: {track.album.release_date}")
                print()
        else:
            print("No tracks found.")
        print()

        # Step 9: Get audio features for a track
        if top_tracks:
            print("8. Getting audio features for top track...")
            top_track = top_tracks[0]
            try:
                audio_features = spotify_client.get_audio_features(top_track.id)
                print(f"Audio features for '{top_track.name}':")
                print(f"  Danceability: {audio_features.danceability:.2f}")
                print(f"  Energy: {audio_features.energy:.2f}")
                print(f"  Valence: {audio_features.valence:.2f}")
                print(f"  Tempo: {audio_features.tempo:.1f} BPM")
                print(f"  Key: {audio_features.key}")
                print(f"  Mode: {'Major' if audio_features.mode else 'Minor'}")
                print(f"  Time Signature: {audio_features.time_signature}/4")
                print(f"  Loudness: {audio_features.loudness:.1f} dB")
                print()
            except Exception as e:
                print(f"Could not get audio features: {e}")
                print()

        # Step 10: Get user's playlists
        print("9. Fetching user's playlists...")
        try:
            playlists = spotify_client.get_user_playlists(user.id, limit=5)
            print("User's playlists:")
            for i, playlist in enumerate(playlists, 1):
                print(f"  {i}. {playlist.name}")
                print(f"     Description: {playlist.description or 'No description'}")
                print(f"     Tracks: {playlist.tracks.total}")
                print(f"     Public: {playlist.public}")
                print(f"     Collaborative: {playlist.collaborative}")
                print()
        except Exception as e:
            print(f"Could not get playlists: {e}")
            print()

        # Step 11: Get recommendations
        if top_artists:
            print("10. Getting track recommendations...")
            try:
                recommendations = spotify_client.get_recommendations(
                    seed_artists=[top_artists[0].id],
                    limit=3
                )
                print(f"Recommendations based on {top_artists[0].name}:")
                for i, track in enumerate(recommendations, 1):
                    print(f"  {i}. {track.name} - {track.artists[0].name}")
                    print(f"     Album: {track.album.name}")
                    print()
            except Exception as e:
                print(f"Could not get recommendations: {e}")
                print()

        print("🎉 Example complete! You can now use the type-safe Spotify client.")
        print()
        print("Available methods:")
        print("- get_current_user() -> UserProfile")
        print("- get_user_top_tracks() -> List[Track]")
        print("- get_user_top_artists() -> List[Artist]")
        print("- search() -> SearchResult")
        print("- get_track() -> Track")
        print("- get_album() -> Album")
        print("- get_artist() -> Artist")
        print("- get_playlist() -> Playlist")
        print("- get_audio_features() -> AudioFeatures")
        print("- get_recommendations() -> List[Track]")
        print("- create_playlist() -> Playlist")
        print("- add_tracks_to_playlist() -> str")
        print("- remove_tracks_from_playlist() -> str")

    except ValueError as e:
        print(f"❌ Authentication failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
