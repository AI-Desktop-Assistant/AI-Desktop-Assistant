import torch
import os
from transformers import BertTokenizer, BertTokenizerFast, AutoModelForCausalLM, AutoTokenizer, AutoConfig
from accelerate import init_empty_weights, infer_auto_device_map, load_checkpoint_and_dispatch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model, tokenizer, = None, None

def load_language_model(model_name):
    # model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16)
    print("Loading Model Config")
    config = AutoConfig.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
    print("Initializing empty model")
    with init_empty_weights():
        model = AutoModelForCausalLM.from_config(config)
    
    device_map = infer_auto_device_map(model, max_memory={0: "10GiB", "cpu": "120GiB"})

    path_to_checkpoints = "C:\\Users\\aidan\\.cache\\huggingface\\hub\\models--meta-llama--Meta-Llama-3-8B-Instruct\\snapshots\\e1945c40cd546c78e41f1151f4db032b271faeaa"
    model = load_checkpoint_and_dispatch(model, path_to_checkpoints,  device_map=device_map, offload_buffers=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    return model, tokenizer, device

def load_classification(model_path):
    model = torch.load(model_path)
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    model.to(device)

    return model, tokenizer, device

def load_entity_recognition_model(model_path):
    model = torch.load(model_path)
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
    
    model.to(device)

    return model, tokenizer, device

def load_email_info_recognizer_model(model_path):
    model = torch.load(model_path)
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')

    model.to(device)
    return model, tokenizer, device

def load_model(model_name_or_path, purpose):
    if purpose == 'response':
        model, tokenizer, device = load_language_model(model_name_or_path)
    elif purpose == 'classification':
        model, tokenizer, device = load_classification(model_name_or_path)
    elif purpose == 'launch':
        model, tokenizer, device = load_entity_recognition_model(model_name_or_path)
    elif purpose == 'email':
        model, tokenizer, device = load_email_info_recognizer_model(model_name_or_path)
    
    return model, tokenizer, device