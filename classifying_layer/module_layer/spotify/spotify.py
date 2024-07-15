from dotenv import load_dotenv    
import os
import base64
from requests import post,get
import json
from config_socketio import socketio

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

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
    json_result = json.loads(result.content)["artists"]["items"]

    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    
    return json_result[0]

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
    print(f"Response:{response}\n:Response:{response.status_code}")
    if response.status_code == 200:
        track_info = json.loads(response.content)
        return track_info
    else:
        return None

import requests

def get_user_authorization():
    # Your client details
    spotify_client_id = client_id
    redirect_uri = 'http://localhost:8888/aiassistant/callback'
    # Scopes enable your application to access specific API endpoints on the user’s behalf
    scope = 'user-read-currently-playing user-read-playback-state'

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
    error = request.args.get('error')
    code = request.args.get('code')
    state = request.args.get('state')
    
    if error:
        return f"Error received: {error}", 400
    if not code:
        return "Code not found in the request", 400

    access_token, refresh_token = get_access_token(code)
    print(access_token, refresh_token)
    track_info = get_currently_playing_track(access_token)
    socketio.emit("response", {"data":track_info, "purpose":"get-track-info"})