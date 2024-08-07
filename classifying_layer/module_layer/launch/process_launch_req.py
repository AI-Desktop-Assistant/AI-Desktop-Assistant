import os
import subprocess
from models.load_model import load_model
from .async_file_search import find_file
from classifying_layer.module_layer.response.response import *
from reception_layer.speech_rec import listen
from classifying_layer.module_layer.handle_confirmation import get_y_or_n
from user_config import get_user_id
from config_socketio import get_app_socket
import sqlite3

model_path = 'models\\app_name_recognizer.pth'
model, tokenizer, device = load_model(model_path, 'launch')

def insert_path(app_name, app_path):
    with sqlite3.connect('users.db') as conn:
        query = 'INSERT INTO remembered_apps (user_id, app_name, app_path, timestamp) VALUES (?, ?, ?, ?)'
        now = datetime.now()
        timestamp = ''
        if now.hour == 0:
            timestamp = f'{now.month}/{now.day}/{now.year} 12:{now.minute} AM'
        elif now.hour <= 12:
            timestamp = f'{now.month}/{now.day}/{now.year} {now.hour}:{now.minute} '
            if now.hour == 12:
                timestamp += f'PM'
            else:
                timestamp += f'AM'
        
        user_id = get_user_id()
        print(f'Inserting: User ID: {user_id}, App Name: {app_name}, App Path: {app_path}')
        conn.execute(query, (user_id, app_name, app_path, timestamp))
        conn.commit()
    socket = get_app_socket()[1]
    socket.emit('response', {'purpose': 'added-path'})

def launch_app(app_name, app_path, unknown=True):
    print(f'Unknown: {unknown}')
    handle_launch_request(app_name)
    # os.system(f'"{best_match["file"]}"')
    subprocess.Popen([app_path], shell=True)
    if unknown:
        alert_remembering_app(app_name)
        insert_path(app_name, app_path)

def launch_best_file(top_files, app_name_from_req):
    best_match = top_files.pop()
    full_app_name = best_match["file"].split("\\")[-1].split('.')[0]
    confidence = best_match["score"]
    print(f'Best Files: {best_match}')
    if confidence > 0.65:
        launch_app(app_name_from_req, best_match["file"])
    elif confidence > 0.1:
        output_response = handle_launch_request(full_app_name, confident=False)
        if output_response["tts"] == "google":
            user_response = listen()
        else:
            user_response = listen()
        y_or_n = get_y_or_n(user_response)
        if y_or_n == "yes":
            launch_app(app_name_from_req, best_match["file"])
        else:
            if len(top_files) != 0:
                launch_best_file(top_files, app_name_from_req)
            else:
                handle_failed_launch()
    else:
        handle_failed_launch()


def parse_app_name(req, model, tokenizer):
    model.eval()
    tokenized_input = tokenizer([req], truncation=True, padding='max_length', is_split_into_words=True, return_tensors="pt")

    input_ids = tokenized_input['input_ids'].to(device)
    attention_mask = tokenized_input['attention_mask'].to(device)
    
    outputs = model(input_ids, attention_mask)

    logits = outputs.logits
    predicted_token_class_ids = logits.argmax(-1)

    tokens = tokenizer.convert_ids_to_tokens(input_ids.squeeze().tolist())

    predicted_tokens_classes = [model.config.id2label[t.item()] for t in predicted_token_class_ids[0]]

    predictions = []
    
    for token, token_class in zip(tokens, predicted_tokens_classes):
        if token_class[-1] != '0' and token != '[PAD]':
            if token.startswith("##"):
                predictions[-1] += token[2:]
            else:
                predictions.append(token)
    

    if predictions:
        return predictions
    else:
        return "No entities found."

def get_app_path(app_name):
    with sqlite3.connect('users.db') as conn:
        query = 'SELECT * FROM remembered_apps WHERE app_name = ? AND user_id = ?'
        cursor = conn.cursor()
        user_id = get_user_id()
        print(f'App Name: {app_name}, User ID: {user_id}')
        cursor.execute(query, (app_name, user_id))
        rows = cursor.fetchall()
        print(f'Rows Queried: {rows}')
        if len(rows) > 0:
            first_row = rows[0]
            print(f'First Row: {first_row}')
            app_path = first_row[3]
            print(f'App Path: {app_path}')
            if len(app_path.split('\\')) == 0:
                print(f'Returning Empty')
                return ''
            else:
                print(f'Returning: {app_path}')
                return app_path
        else:
            return ''

def process_launch_req(req):
    print(f'Getting app name from req: {req}')
    app_name_from_req = " ".join(parse_app_name(req, model, tokenizer))
    print(f'App Name: {app_name_from_req}')
    if app_name_from_req != "N o   e n t i t i e s   f o u n d .":    
        print(f'Getting App Path from App Name: {app_name_from_req}')
        app_path = get_app_path(app_name_from_req)
        if app_path == '':
            file_search_feedback(app_name_from_req)
            top_files = find_file(app_name_from_req)
            if len(top_files) != 0:
                launch_best_file(top_files, app_name_from_req)
            else:
                handle_failed_launch()
        else:
            launch_app(app_name_from_req, app_path, unknown=False)
        