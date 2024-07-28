import torch
from transformers import BertTokenizer, BertTokenizerFast, AutoModelForCausalLM, AutoTokenizer
from .module_layer.launch.process_launch_req import *
from models.load_model import load_model
from .module_layer.email.process_email_request import process_email_req
from .module_layer.task.process_task_req import process_task_req

model_path = 'models\\module_classification_model.pth'
model, tokenizer, device = load_model(model_path, 'classification')

def classify(req):
    labels_to_index = {'email': 0, 'generic': 1, 'launch': 2, 'spotify': 3, 'task': 4, 'weather': 5}
    model.eval()
    
    tokenized_input = tokenizer([req], padding=True, truncation=True, return_tensors="pt")
    
    input_ids = tokenized_input['input_ids'].to(device)
    attention_mask = tokenized_input['attention_mask'].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask)
    
    logits = outputs.logits
    predicted_label_id = torch.argmax(logits, dim=1)
    
    for label, idx in labels_to_index.items():
        if predicted_label_id == idx:
            predicted_module = label
        
    return predicted_module

def classify_user_request(req, socket):
    module = classify(req)
    print(f'Chosen Module: {module}')
    if module == 'launch':
        status = process_launch_req(req)
    # elif module == 'weather':
    #     weather(input)
    elif module == 'email':
        status = process_email_req(req, socket)
    elif module == 'task':
        process_task_req(req)
    # elif module == 'spotify':
    #     spotify(input)
    # elif module == 'generic':
    #     generic(input)
    return module