import time
from transformers import pipeline, set_seed
import random
import json
from reception_layer.speech_rec import say

start = time.time()
generator = pipeline('text-generation', model='gpt2')
set_seed(42)
end = time.time()
random.seed(time.time())
print(f'Time to load: {end-start}')

def generate_response(prompt, max_length=35):
    print(f'Starting gen on Prompt: {prompt}')
    start = time.time()
    responses = generator(prompt, max_length=max_length, num_return_sequences=5, temperature=0.551)
    end = time.time()
    print(f'Time to generate: {end-start}')
    # response = response[len(prompt):].strip()
    # return response.split('.')[0] + '.'
    return responses
    # return response

def handle_launch_request(full_app_name, confident=True):
    with open('reception_layer\\classifying_layer\\module_layer\\response\\templates\\templates.json') as f:
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
    with open('reception_layer\\classifying_layer\\module_layer\\response\\templates\\templates.json') as f:
        templates = json.load(f)["search"]

    response = random.choice(templates).replace("[given_name]", given_name)
    return say(response)    

