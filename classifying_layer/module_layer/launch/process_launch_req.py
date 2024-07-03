import os
import subprocess
from transformers import BertTokenizerFast
from models.load_model import load_model
from .async_file_search import find_file
from classifying_layer.module_layer.response.response import *
from reception_layer.speech_rec import listen
from classifying_layer.module_layer.handle_confirmation import get_y_or_n

model_path = 'models\\app_name_recognizer.pth'
model, tokenizer, device = load_model(model_path, 'launch')

def launch_best_file(top_files):
    best_match = top_files.pop()
    full_app_name = best_match["file"].split("\\")[-1].split('.')[0]
    confidence = best_match["score"]
    if confidence > 0.65:
        handle_launch_request(full_app_name)
        # os.system(f'"{best_match["file"]}"')
        subprocess.Popen([best_match["file"]], shell=True)
    else:
        output_response = handle_launch_request(full_app_name, confident=False)
        if output_response["tts"] == "google":
            user_response = listen()
        else:
            user_response = listen()
        y_or_n = get_y_or_n(user_response)
        if y_or_n == "yes":
            handle_launch_request(full_app_name)
            # os.system(f'"{best_match["file"]}"')
            subprocess.Popen([best_match["file"]], shell=True)
        else:
            if len(top_files) != 0:
                launch_best_file(top_files)
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

def process_launch_req(req):
    app_name_from_req = " ".join(parse_app_name(req, model, tokenizer))
    if app_name_from_req != "N o   e n t i t i e s   f o u n d .":    
        file_search_feedback(app_name_from_req)
        top_files = find_file(app_name_from_req)
        if len(top_files) != 0:
            launch_best_file(top_files)
        else:
            handle_failed_launch()
        