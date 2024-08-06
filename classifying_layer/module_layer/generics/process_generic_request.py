def process_generic_req(req):
    from models.load_model import load_model
from classifying_layer.module_layer.response.response import *
import sqlite3
import time 

generic_info_model_path = 'models\\generic_info_recognizer.pth'
generic_intent_model_path = 'models\\generic_intent_recognizer.pth'
generic_entity_model_path = 'models\\generic_entity_recognizer.pth'

# Load models for processing generic requests
generic_info_model, tokenizer, device = load_model(generic_info_model_path, 'generic')
generic_intent_model, tokenizer, device = load_model(generic_intent_model_path, 'generic')
generic_entity_model, tokenizer, device = load_model(generic_entity_model_path, 'generic')

def predict_tokens(req, model):
    tokenized_input = tokenizer([req], truncation=True, padding='max_length', is_split_into_words=True, return_tensors="pt")
    input_ids = tokenized_input['input_ids'].to(device)
    attention_mask = tokenized_input['attention_mask'].to(device)
    outputs = model(input_ids, attention_mask)
    logits = outputs.logits
    predicted_token_class_ids = logits.argmax(-1)
    tokens = tokenizer.convert_ids_to_tokens(input_ids.squeeze().tolist())
    predicted_token_classes = [model.config.id2label[t.item()] for t in predicted_token_class_ids[0]]
    return tokens, predicted_token_classes

def parse_generic_entities(req):
    generic_entity_model.eval()
    tokens, predict_tokens_classes = predict_tokens(req, generic_entity_model)
    entity_predictions = []
    for token, token_classes in zip(tokens, predict_tokens_classes):
        if token_classes[-1] != '0' and token != '[PAD]' and token != '[CLS]' and token != '[SEP]':
            if token.startswith("##"):
                entity_predictions[-1] += token[2:]
            else:
                entity_predictions.append(token)
    return entity_predictions

def parse_generic_intent(req):
    generic_intent_model.eval()
    tokens, predicted_tokens_classes = predict_tokens(req, generic_intent_model)
    intents = {}
    for token, token_class in zip(tokens, predicted_tokens_classes):
        if token_class[-1] != 'O' and token != '[PAD]' and token != '[CLS]' and token != '[SEP]':
            if token_class not in intents:
                intents[token_class] = []
            if token.startswith('##'):
                intents[token_class][-1] += token[2:]
            else:
                intents[token_class].append(token)
    return intents

def handle_missing_information(information_type):
    response = get_information_from_user(information_type)
    if response == '':
        response = get_information_from_user(information_type)
        if response == '':
            return ''
    return response

def get_information_from_user(info_type):
    # Placeholder for function to get missing information from the user
    # In a real application, this could involve user interaction, additional prompts, etc.
    return input(f"Please provide {info_type}: ")

def respond_to_generic_request(entities, intents):
    # Placeholder for response generation based on parsed entities and intents
    response = "Handling request with the following details:\n"
    response += f"Entities: {entities}\n"
    response += f"Intents: {intents}\n"
    # Add more sophisticated response generation here
    return response

def process_generic(req):
    # Parse entities and intent from the request
    entities = parse_generic_entities(req)
    intents = parse_generic_intent(req)
    
    # Handle cases where necessary information is missing
    if not entities:
        entities = handle_missing_information('entities')
    if not intents:
        intents = handle_missing_information('intents')
    
    # Respond to the generic request
    response = respond_to_generic_request(entities, intents)
    return response

# Example usage
request = "Whats the weather like in Miami right now ."
response = process_generic(request)
print(response)


