import torch
from transformers import BertTokenizer

def classify(req, model):
    labels_to_index = {'no': 0, 'yes': 1}
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    
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
    model = torch.load('reception_layer\\models\\yes_no_classification_model.pth')
    module = classify(req, model)
    print(f'Chosen Module: {module}')
    return module
    