from dotenv import load_dotenv    
import os
import base64
from requests import post,get,put
import json
from config_socketio import get_app_socket
from json import JSONDecodeError

from flask import request

load_dotenv()

app, socketio = get_app_socket()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

user_tokens = {}
current_user_id = None

def set_current_user_id(user_id):
    global current_user_id
    current_user_id = user_id

def store_tokens(user_id, access_token, refresh_token):
    user_tokens[user_id] = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

def get_stored_tokens(user_id):
    return user_tokens.get(user_id)

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)

    if 'artists' in json_result and 'items' in json_result['artists']:
        if len(json_result['artists']['items']) == 0:
            print("No artist with this name exists...")
            return None
        
        return json_result['artists']['items'][0]
    else:
        print("Unexpected JSON structure:", json_result)
        return None

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def search(artist_name):
    token = get_token()
    result = search_for_artist(token, artist_name)
    if result:
        artist_id = result["id"]
        songs = get_songs_by_artist(token, artist_id)
        for idx, song in enumerate(songs):
            print(f"{idx + 1}. {song['name']}")
        return result
    else:
        print("Artist not found.")

def get_currently_playing_track(token):
    url = "https://api.spotify.com/v1/me/player/currently-playing"
    headers = get_auth_header(token)
    response = get(url, headers=headers)
    if response.status_code == 200:
        track_info = json.loads(response.content)
        return track_info
    elif response.status_code == 204:
        print("No track currently playing.")
        return None
    else:
        print(f"Failed to get currently playing track: {response.status_code}")
        return None

import requests

def get_user_authorization():
    # Your client details
    spotify_client_id = client_id
    redirect_uri = 'http://localhost:8888/aiassistant/callback'
    # Scopes enable your application to access specific API endpoints on the user’s behalf
    scope = 'user-read-currently-playing user-read-playback-state user-modify-playback-state app-remote-control'

    # Construct the URL
    auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={spotify_client_id}&scope={scope}&redirect_uri={redirect_uri}"

    return auth_url

def get_access_token(code):
    token_url = 'https://accounts.spotify.com/api/token'
    spotify_client_id = client_id
    spotify_client_secret = client_secret
    redirect_uri = 'http://localhost:8888/aiassistant/callback'

    # Request body
    body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": spotify_client_id,
        "client_secret": spotify_client_secret
    }

    # Make the POST request
    response = requests.post(token_url, data=body)
    token_info = response.json()
    return token_info['access_token'], token_info['refresh_token']

def spotify_callback(request):
    try:
        print("Callback request received")
        error = request.args.get('error')
        code = request.args.get('code')
        state = request.args.get('state')

        if error:
            print(f"Error in Spotify authorization: {error}")
            return f"Error received: {error}", 400
        if not code:
            print("No code found in the request")
            return "Code not found in the request", 400

        access_token, refresh_token = get_access_token(code)
        store_tokens(current_user_id, access_token, refresh_token)  # Use global current_user_id
        
        print(f"Access Token: {access_token}")
        print(f"Refresh Token: {refresh_token}")

        track_info = get_currently_playing_track(access_token)
        if track_info:
            # Extracting necessary information
            simplified_info = {
                'track_name': track_info['item']['name'],
                'artist_name': ", ".join([artist['name'] for artist in track_info['item']['artists']]),
                'album_name': track_info['item']['album']['name'],
                'album_image': track_info['item']['album']['images'][0]['url'],
                'progress_ms': track_info['progress_ms'],
                'duration_ms': track_info['item']['duration_ms'],
                'is_playing': track_info['is_playing']
            }

            print(f"Simplified Track Info: {simplified_info}")

            socketio.emit("get-currently-playing-response", {"data": simplified_info, "purpose": "get-track-info"})
        else:
            print("No track currently playing")
            socketio.emit("response", {"data": "No track currently playing", "purpose": "get-track-info"})
        return "Callback handled successfully", 200
    except Exception as e:
        print(f"Error in callback: {e}")
        return f"Internal Server Error: {e}", 500
    
def pause_playback(token):
    url = "https://api.spotify.com/v1/me/player/pause"
    headers = get_auth_header(token)
    response = put(url, headers=headers)
    if response.status_code in [200, 204]:
        return "Playback paused."
    else:
        try:
            error_message = response.json().get('error', {}).get('message', 'No error message')
        except ValueError:
            error_message = 'Invalid response received'
        return f"Failed to pause playback: {response.status_code} - {error_message}"

def resume_playback(token):
    url = "https://api.spotify.com/v1/me/player/play"
    headers = get_auth_header(token)
    response = put(url, headers=headers)
    if response.status_code in [200, 204]:
        return "Playback resumed."
    else:
        try:
            error_message = response.json().get('error', {}).get('message', 'No error message')
        except ValueError:
            error_message = 'Invalid response received'
        return f"Failed to resume playback: {response.status_code} - {error_message}"

def play_next_track(token):
    url = "https://api.spotify.com/v1/me/player/next"
    headers = get_auth_header(token)
    response = post(url, headers=headers)
    if response.status_code == 204:
        return "Playing next track."
    elif response.status_code == 200:
        return "Playing next track."
    else:
        return f"Failed to play next track: {response.status_code}"