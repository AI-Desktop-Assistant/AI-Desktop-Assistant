import torch
import os
from transformers import BertTokenizerFast
from .threaded_file_search import find_file

def parse_app_name(req, model):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
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
                predictions[-1] += token[2:]  # Append to the last word if it's a subword
            else:
                predictions.append(token)
    

    if predictions:
        return predictions
    else:
        return "No entities found."

def process_launch_req(req):
    model = torch.load('reception_layer\\models\\app_name_recognizer.pth')
    app_name_from_req = " ".join(parse_app_name(req, model))
    best_match = find_file(app_name_from_req)
    os.system(f'"{best_match["file"]}"')
        
