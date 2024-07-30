import os
import sys
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from threading import Thread
from reception_layer.speech_rec import listen
from classifying_layer.classify_req import classify_user_request
from user_config import *
from config_socketio import create_app_socket
from classifying_layer.module_layer.weather.process_weather_req import receive_weather_data
from classifying_layer.module_layer.response.response import report_weather

app, socketio = create_app_socket()

from classifying_layer.module_layer.spotify.spotify import search, get_user_authorization, get_currently_playing_track, spotify_callback, get_token, pause_playback, resume_playback, play_next_track, get_stored_tokens, set_current_user_id

os.environ['USE_FLASH_ATTENTION'] = '1'
logged_in = True
current_user_id = ''
current_username = ''
current_email = ''

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_message(data):   
    global current_user_id
    if data['purpose'] == 'search':
        result = search(data['data'])
        emit('response', {'data': result,'purpose':'search'})
    elif data['purpose'] == "get-token":
        # token = get_token()
        auth_url = get_user_authorization()
        # track_info = get_currently_playing_track(token)
        emit('response', {'data': auth_url,'purpose':'get-token'})
    elif data['purpose'] == 'get-currently-playing':
        tokens = get_stored_tokens(current_user_id)
        if tokens:
            track_info = get_currently_playing_track(tokens['access_token'])
            if track_info:
                emit("get-currently-playing-response", {"data": track_info, "purpose": "get-track-info"})
        else:
            emit("response", {"data": "No token found for user", "purpose": "get-currently-playing"})
    elif data['purpose'] == 'get-weather-data':
        receive_weather_data(data)
    elif data['purpose'] == 'control-playback':
        tokens = get_stored_tokens(current_user_id)
        if tokens:
            action = data['action']
            if action == 'pause':
                result = pause_playback(tokens['access_token'])
            elif action == 'resume':
                result = resume_playback(tokens['access_token'])
            elif action == 'next':
                result = play_next_track(tokens['access_token'])
            emit("control-playback-response", {"data": result, "purpose": "control-playback"})
        else:
            emit("control-playback-response", {"data": "No token found for user", "purpose": "control-playback"})
            
def run_flask():
    socketio.run(app, port=8888, debug=False, allow_unsafe_werkzeug=True)

def main_loop(user_id, username, email, socket):
    global current_user_id
    global current_username
    global current_email

    current_user_id = user_id
    current_username = username
    current_email = email
    set_current_user_id(current_user_id)
    print('Starting Main Loop')
    while True:
        if logged_in:
            # listen for input
            try:
                input = listen()
            except:
                continue
            # input = "Compose an update email to the customer service team and CC the support manager and quality assurance lead and BCC the technical support lead and IT manager"
            # after getting input classify the model
            module = classify_user_request(input, socket)
            # delve into selected module deeper

@app.route('/update_email', methods=['POST'])
def update_username():
    print('updating username')
    global current_username
    new_username = request.json.get('username')
    if new_username:
        print('updated email')
        set_username(new_username)
        current_username = new_username
        return jsonify(success=True, message="Username updated successfully!")
    return jsonify(success=False, message="Unable to update username in main.py")

@app.route('/update_username', methods=['POST'])
def update_email():
    print('updating email')
    global current_email
    new_email = request.json.get('email')
    if new_email:
        print('updated email')
        set_user_email(new_email)
        current_email = new_email
        return jsonify(success=True, message="Email updated successfully!")
    return jsonify(success=False, message="Unable to update email in main.py")

@app.route('/login', methods=['POST'])
def update_login_status():
    print('updating login status')
    global logged_in
    login_status = request.json.get('login')
    if login_status:
        logged_in = login_status
        print('updated Login status')
        return jsonify(success=True, message="Login status updated successfully!")
    return jsonify(success=False, message="Unable to update login_status in main.py")

@app.route('/aiassistant/callback')
def callback():
    return spotify_callback(request)

@app.route('/report_weather', methods=['POST'])
def report_weather_route():
    data = request.json
    city = data.get('city')
    temperature = data.get('temperature')
    if city and temperature:
        report_weather(city, temperature)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

@app.route('/pause', methods=['POST'])
def pause_route():
    token = request.json.get('token')
    result = pause_playback(token)
    return jsonify({"message": result})

@app.route('/resume', methods=['POST'])
def resume_route():
    token = request.json.get('token')
    result = resume_playback(token)
    return jsonify({"message": result})

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python main.py <user_id> <username> <email>")
        sys.exit(1)
    current_user_id = sys.argv[1]
    current_username = sys.argv[2]
    current_email = sys.argv[3]
    print(f'User ID: {current_user_id}, Username: {current_username}, Email: {current_email}')
    print("\nStarting flask\n")
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    configure_user(current_user_id, current_email, current_username)
    main_loop(current_user_id, current_username, current_email, socketio)