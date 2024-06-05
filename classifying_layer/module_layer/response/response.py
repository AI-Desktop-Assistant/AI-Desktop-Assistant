import time
import random
import json
from models.load_model import load_model
from huggingface_hub import login
from reception_layer.speech_rec import say

login(token="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", add_to_git_credential=True)

# start = time.time()
# model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
# model, tokenizer, device = load_model(model_name, 'response')
# terminators = [tokenizer.eos_token_id, tokenizer.convert_tokens_to_ids("<|eot_id|>")]
# end = time.time()
# print(f'Time to load: {end-start}')
random.seed(time.time())

# def pass_prompt_to_model(prompt):
#     tokenized_inputs = tokenizer.apply_chat_template(prompt, add_generation_prompt=True, return_dict=True, return_tensors="pt")
#     input_ids, attention_mask = tokenized_inputs["input_ids"], tokenized_inputs["attention_mask"]
#     outputs = model.generate(input_ids, attention_mask=attention_mask, max_new_tokens=256, eos_token_id=terminators, do_sample=True, temperature=0.6, top_p=0.9)
#     response = outputs[0][input_ids.shape[-1]:]
#     return tokenizer.decode(response, skip_special_tokens=True)

# def generate_response(prompt):
#     print(f'Starting gen on Prompt: {prompt}')
#     start = time.time()
#     response = pass_prompt_to_model(prompt)
#     end = time.time()
#     print(f'Time to generate: {end-start}')
#     # response = response[len(prompt):].strip()
#     # return response.split('.')[0] + '.'
#     print(response)
#     return response

def handle_launch_request(full_app_name, confident=True):
    with open('classifying_layer\\module_layer\\response\\templates\\templates.json') as f:
        templates = json.load(f)["launch"]
    if confident:
        response = random.choice(templates["confident"]) + full_app_name
    else:
        response = random.choice(templates["not confident"]).replace("[file_name]", full_app_name)
    return say(response)

def handle_failed_launch():
    response = "Sorry, I couldnt find the file you wanted."
    return say(response)

def file_search_feedback(given_name):
    with open('classifying_layer\\module_layer\\response\\templates\\templates.json') as f:
        templates = json.load(f)["search"]

    response = random.choice(templates).replace("[given_name]", given_name)
    # messages = [
    #     {"role": "system", "content": f"You are an AI Desktop Assistant and are searching through the users files for this app: {given_name}"},
    #     {"role": "user", "content": "What are you doing?"}
    # ]
    # response = generate_response(messages)
    return say(response)    
