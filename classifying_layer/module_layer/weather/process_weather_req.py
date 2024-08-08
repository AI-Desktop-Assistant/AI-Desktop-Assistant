# from models.load_model import load_model
import torch
from config_socketio import get_app_socket
from transformers import BertTokenizer, BertTokenizerFast, AutoModelForCausalLM, AutoTokenizer, AutoConfig

weather_model_path = 'models\\weather_intent.pth'
# weather_model, tokenizer, device = load_model(weather_model_path, 'weather')
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

def process_weather_request(req):
    weather_model, tokenizer, device = load_weather_intent_model(weather_model_path)
    tokens, predicted_token_classes = predict_tokens(req, weather_model, tokenizer)
    sifted_result = sift_output(tokens, predicted_token_classes)
    result = ' '.join(sifted_result)
    send_sift_data(result)

def load_weather_intent_model(model_path):
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
    return sift

def send_sift_data(sift):
    if sift:
        print(f'Sending weather data: {sift}')
        app, socketio = get_app_socket()
        socketio.emit("get-weather", {"data": sift, "purpose": "get-weather-info"})

def receive_weather_data(weatherData):
    print(weatherData)