import os
import sys
import time
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from threading import Thread
from reception_layer.speech_rec import *
from classifying_layer.module_layer.response.response import *
from classifying_layer.classify_req import classify_user_request
from classifying_layer.module_layer.task.process_task_req import *
from user_config import *
from config_socketio import create_app_socket
from classifying_layer.module_layer.weather.process_weather_req import receive_weather_data
from classifying_layer.module_layer.response.response import report_weather
from classifying_layer.module_layer.email.email_handler import send_email
from reception_layer.speech_rec import *

app, socketio = create_app_socket()

from classifying_layer.module_layer.spotify.spotify import search_for_track, get_user_authorization, get_currently_playing_track, spotify_callback, get_token, pause_playback, resume_playback, play_next_track, get_stored_tokens, set_current_user_id, get_user_playlists, start_playback


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
    print(f'Flask Received message: {data}')
    global current_user_id
    if data['purpose'] == 'search':
        tokens = get_stored_tokens(current_user_id)
        if tokens:
            result = search_for_track(tokens['access_token'], data['data'])
            if result:
                track_uri = result['uri']
                track_info = {
                    'name': result['name'],
                    'artists': [artist['name'] for artist in result['artists']],
                    'album': result['album']['name'],
                    'album_image': result['album']['images'][0]['url']
                }
                start_playback(tokens['access_token'], track_uri)
                emit('response', {'data': track_info, 'purpose':'search'})
            else:
                emit('response', {'data': 'Track not found', 'purpose':'search'})
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
    elif data['purpose'] == 'chat':
        req = data['data']
        if req != '':
            # module = classify_user_request(req)
            set_recieved_message(req)
    elif data['purpose'] == 'email':
        print('Sending email')
        try:
            send_email(data['email'], data['appPassword'], data['recipients'], data['subject'], data['body'])
        except Exception as e:
            print(e)
    elif data['purpose'] == 'tasks-today':
        print('Getting Tasks Today For Table')
        tasks_today = get_tasks_today()
        tasks = []
        dates = []
        times = []
        repeatings = []
        print(f'Tasks Today: {tasks_today}')
        for task in tasks_today:
            print(f'Task: {task}')
            tasks.append(task[4])
            dates.append(task[2])
            times.append(task[3])
            repeatings.append(task[5])
            print(f'Building Tasks Today: {tasks_today}')
        print(f'Tasks Sending to Table: {tasks_today}')
        socketio.emit('response', {'purpose': 'tasks-today-response', 'dates': dates, 'times': times, 'tasks': tasks, 'repeatings': repeatings})
    elif data['purpose'] == 'volume':
        change_volume(data['data'])
    elif data['purpose'] == 'voice':
        change_voice(data['data'])
    elif data['purpose'] == 'signout':
        os._exit(1)
    elif data['purpose'] == 'set-task':
        task_date = data['taskDate']
        task_time = data['taskTime']
        date = datetime.strptime(task_date, '%Y-%m-%d')
        time = datetime.strptime(task_time, '%H:%M')
        print(f"Setting Task With: {data['taskDetails']}, {date}, {time}, {True if 'AM' in data['taskTime'] else False}")
        set_task(data['taskDetails'], date, time, '', True if 'AM' in data['taskTime'] else False)
        socketio.emit('response', {'purpose': 'task-set-response', 'success': True, 'message': 'Task Successfully Set'})

def run_flask():
    socketio.run(app, port=8888, debug=False, allow_unsafe_werkzeug=True)

def main_loop(user_id, username, email):
    global current_user_id
    global current_username
    global current_email

    current_user_id = user_id
    current_username = username
    current_email = email
    set_current_user_id(current_user_id)
    print('Starting Main Loop')
    first_iter = True
    while True:
        if logged_in:
            # listen for input
            try:
                print('Checking remind tasks')
                remind_tasks()
                if first_iter:
                    print('Listening For Wake Word First Iteration')
                    wake_word_detected = listen_for_wake_word(ready='I am ready to provide assistance')
                    print(f'Listen For Wake Word Output: {wake_word_detected}')
                    first_iter = False
                else:
                    print('Listening For Wake Word')
                    wake_word_detected = listen_for_wake_word()
                    print(f'Listen For Wake Word Output: {wake_word_detected}')
                if wake_word_detected:
                    print('Wake Word Detected')
                    if isinstance(wake_word_detected, str):
                        input = wake_word_detected
                    else:
                        input = listen(ready='How can I help?')
                    if input != 'Sorry, I didnt understand your request':
                        module = classify_user_request(input)
                    wake_word_detected = False
                else:
                    print('No wake word detected')
            except Exception as e:
                print(e)


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

@app.route('/get_playlists', methods=['POST'])
def get_playlists():
    tokens = get_stored_tokens(current_user_id)
    if tokens:
        playlists = get_user_playlists(tokens['access_token'])
        return jsonify(playlists=playlists)
    else:
        return jsonify(error="No token found for user"), 400
    
@app.route('/start_playback', methods=['POST'])
def start_playback_route():
    tokens = get_stored_tokens(current_user_id)
    if tokens:
        uri = request.json.get('uri')
        uri_type = request.json.get('uri_type', 'track')
        result = start_playback(tokens['access_token'], uri, uri_type)
        return jsonify(message=result)
    else:
        return jsonify(error="No token found for user"), 400
    
@app.route('/search', methods=['POST'])
def search():
    data = request.json
    purpose = data.get('purpose')
    search_query = data.get('data')
    
    if purpose == 'search':
        tokens = get_stored_tokens(current_user_id)
        if tokens:
            result = search_for_track(tokens['access_token'], search_query)
            if result:
                track_uri = result['uri']
                track_info = {
                    'name': result['name'],
                    'artists': [artist['name'] for artist in result['artists']],
                    'album': result['album']['name'],
                    'album_image': result['album']['images'][0]['url']
                }
                playback_result = start_playback(tokens['access_token'], track_uri, uri_type="track")
                if "Playback started" in playback_result:
                    return jsonify(data=track_info)
                else:
                    return jsonify(error=playback_result)
            else:
                return jsonify(data='Track not found')
    return jsonify(error='Invalid request'), 400

if __name__ == "__main__":
    try:
        print(f'Argv: {sys.argv}')
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
        time.sleep(5)
        print('Configuring user')
        configure_user(current_user_id, current_email, current_username)
        print(f'Greeting User: {current_username}')
        greeting(current_username)
        print('Outputting Tasks Today')
        output_tasks_today()
        main_loop(current_user_id, current_username, current_email)
    except Exception as e:
        print(e)