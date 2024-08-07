import torch
from transformers import BertTokenizerFast
from config_socketio import get_app_socket
from classifying_layer.module_layer.spotify.spotify import pause_playback, resume_playback, play_next_track, get_stored_tokens, current_user_id
from user_config import get_user_id

spotify_model_path = 'models\\spotify_command_model.pth'
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def predict_tokens(req, model, tokenizer):
    tokenized_input = tokenizer([req], truncation=True, padding='max_length', is_split_into_words=True, return_tensors="pt")
    input_ids = tokenized_input['input_ids'].to(device)
    attention_mask = tokenized_input['attention_mask'].to(device)
    
    outputs = model(input_ids, attention_mask)
    logits = outputs.logits
    predicted_token_class_ids = logits.argmax(-1)

    tokens = tokenizer.convert_ids_to_tokens(input_ids.squeeze().tolist())
    predicted_tokens_classes = [model.config.id2label[t.item()] for t in predicted_token_class_ids[0]]

    return tokens, predicted_tokens_classes

def process_spotify_request(req):
    model, tokenizer, device = load_spotify_intent_model(spotify_model_path)
    tokens, predicted_token_classes = predict_tokens(req, model, tokenizer)
    command = sift_output(tokens, predicted_token_classes)
    execute_spotify_command(command)

def load_spotify_intent_model(model_path):
    model = torch.load(model_path)
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
    model.to(device)
    return model, tokenizer, device

def sift_output(tokens, predicted_token_classes):
    sift = []
    for token, predicted_token_class in zip(tokens, predicted_token_classes):
        if token != "[CLS]" and token != "[SEP]" and token != "[PAD]" and predicted_token_class != "LABEL_0":
            if token.startswith('##'):
                sift[-1] += token[2:]
            else:
                sift.append(token)
    return sift[0] if sift else ""

def execute_spotify_command(command):
    print("checking for playback command...")
    app, socketio = get_app_socket()
    user_id = get_user_id()
    tokens = get_stored_tokens(user_id)
    if tokens:
        if command == 'pause':
            result = pause_playback(tokens['access_token'])
        elif command == 'resume':
            result = resume_playback(tokens['access_token'])
        elif command == 'skip':
            result = play_next_track(tokens['access_token'])
        else:
            result = "Unknown command"
            print(f"Error checking command {command}...")
        
        socketio.emit("control-playback-response", {"data": result, "purpose": "control-playback"})
    else:
        socketio.emit("control-playback-response", {"data": "No token found for user", "purpose": "control-playback"})