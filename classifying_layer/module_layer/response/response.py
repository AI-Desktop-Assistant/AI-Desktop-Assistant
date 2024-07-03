import time
import random
import json
from models.load_model import load_model
from huggingface_hub import login
from reception_layer.speech_rec import *

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

def alert_creating_contact(recipient, recipient_email):
    response = f'Creating a contact for {recipient}, with email {recipient_email}'
    say(response)

def ask_to_create_contact(recipient, recipient_email):
    response = f'Would you like to create a contact for {recipient} with email address {recipient_email}'
    say(response)
    user_response = listen()
    return user_response

def get_email_from_user(recipient):
    response = f"I couldn't find a contact for {recipient}, can you tell me their email?"
    say(response)
    user_response = listen()
    return user_response

def get_recipients_from_user():
    response = "Sorry I couldn't find an email recipient, can you tell me who this email intended for?"
    say(response)
    user_response = listen()
    return user_response

def get_intent_from_user():
    response = 'Could you provide some more detail on the intent of the email?'
    say(response)
    user_response = listen()
    return user_response

def prompt_to_update_footer():
    response = 'It looks like you have not set an email signature, please go to your settings and set an email signature to send emails.'
    say(response)

def alert_not_understood():
    response = 'Sorry I didnt catch that.'
    say(response)

def prompt_user_to_retry():
    response = 'Try requesting again'
    say(response)

def prompt_user_to_update_email():
    response = 'Please update your email in your settings to send an email'
    say(response)

def ask_to_show_email(op=''):
    if op == 'send':
        response = 'Would you like to see the email before sending?'
    else:
        response = 'Would you like to see the drafted email?'
    say(response)
    user_response = listen()
    return user_response

def respond_showing_email():
    response = 'Ok, displaying your email.'
    say(response)

def respond_ending_request_chain():
    response = 'Ok, let me know if i can help you with anything else.'
    say(response)

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
