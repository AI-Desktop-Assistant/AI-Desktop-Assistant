import torch
from models.load_model import load_model

model_path = 'models\\yes_no_classification_model.pth'
model, tokenizer, device = load_model(model_path, 'classification')

def classify(req):
    labels_to_index = {'no': 0, 'yes': 1}
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

def get_y_or_n(req):
    module = classify(req)
    print(f'Chosen Module: {module}')
    return module
    