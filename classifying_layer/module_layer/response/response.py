from datetime import datetime, timedelta
import time
import random
import json
from models.load_model import load_model
from huggingface_hub import login
from reception_layer.speech_rec import *
from nltk.corpus import wordnet as wn

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

def alert_remembering_app(app_name):
    response = f'Remembering path to {app_name} for next launch'
    say(response)

def handle_invalid_time():
    response = 'When would you like this reminder to be set for?'
    return say(response)

def prompt_for_missing_date_or_time(val_date, val_time):
    user_input = 'date '
    if not val_time and not val_date:
        user_input += 'and time '
    elif not val_time:
        user_input = 'time '
    
    response = f'Could you provide me with the {user_input} for your reminder'
    say(response)
    user_response = listen()

    return user_response

def output_tasks_to_user(response, confirm=False):
    print('Outputting tasks')
    say(response)
    user_response = ''
    if confirm:
        user_response = listen()
    return user_response

def alert_reading_remaining_tasks(plural):
    plural_str = 'remaining tasks are, ' if plural else 'last task is, '
    response = f'Ok. Your {plural_str}'
    say(response)
    
def get_pos(word):
    print(f'Getting Part of Speech for word: {word}')
    synsets = wn.synsets(word)
    print(f'Part of speech: {synsets[0].pos()}')
    if not synsets:
        return None
    return synsets[0].pos()

def intent_as_response(intent):
    if intent != '':
        first_word = intent.split()[0]
        pos = get_pos(first_word)
        if pos == 'n':
            response = 'for '
        elif pos == 'v':
            response = 'to ' if not first_word.endswith('ing') else 'for '
        else:
            response = 'to '
            
        if 'my' in intent:
            intent = intent.replace('my', 'your')
        response += intent
    else:
        response = ''
    return response

def alert_task_set(intent, task_date, hour, minute, is_am, repeat, task_ref):
    print(f'Alerting Task Set: Intent: {intent}, Date: {task_date}, Hour: {hour}, Minute: {minute}, Is AM: {is_am}, Repeat: {repeat}, Task Ref: {task_ref}')
    print(f'Intent: {intent}')
    intent_response =  intent_as_response(intent)
    if intent == '':
        response = 'I have set an alarm '
    elif 'remind' in task_ref and intent != '':
        if 'to ' in intent_response:
            response = f'Reminding you {intent_response} '
        else:
            response = f'Setting a reminder {intent_response} '
    else:
        response = f'I have set a task {intent_response} '
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    two_weeks_date = today + timedelta(weeks=2)
    time_str = f'{hour}:{minute} '
    time_str += f'AM' if is_am else 'PM'
    time_obj = datetime.strptime(time_str, '%I:%M %p')
    if today.year == task_date.year and today.month == task_date.month and today.day == task_date.day and not repeat:
        print('Task set for today')
        response += 'in '
        diff = time_obj - today
        hour_in_seconds = 3600
        diff_hours = diff.seconds // hour_in_seconds
        print(f'Difference 24 conv - today.hour: {diff_hours}')
        if diff_hours > 0:
            response += f'{diff_hours} hour'
            if diff_hours > 1:
                response += 's '
            else: 
                response += ' '
        diff_minutes = diff.seconds % hour_in_seconds
        print(f'Seconds % hour in seconds: {diff_minutes}')
        diff_minutes = (diff_minutes // 60) + 1
        print(f'Diff Minutes: {diff_minutes}')
        if diff_minutes > 0:
            if 'hour' in response:
                response += 'and '
            response += f'{diff_minutes} minutes '
    elif tomorrow.year == task_date.year and tomorrow.month == task_date.month and tomorrow.day == task_date.day and not repeat:
        response += 'tomorrow '
    elif task_date <= two_weeks_date:
        one_week_date = today + timedelta(weeks=1)
        if repeat:
            response += ' every '
        elif task_date >= one_week_date:
            response += 'next '
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        print(f'Weekday num: {task_date.weekday()}')
        response += f'{days[task_date.weekday()]} '
    else:
        response += f'on '
        months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'november', 'december']
        month = months[task_date.month - 1]
        response += f'{month} {task_date.day} '
        if task_date.year != today.year:
            response += f'{task_date.year} '
    response += 'at '
    response += f'{hour}:{minute} '
    if is_am:
        response += 'in the morning'
    else:
        if hour < 6 or hour == 12:
            response += 'in the afternoon'
        elif hour < 9:
            response += 'in the evening'
        else:
            response += 'at night'
    say(response)

def handle_failed_launch():
    response = "Sorry, I couldn't find the file you wanted."
    return say(response)

def alert_creating_contact(recipient, recipient_email):
    response = f'Creating a contact for {recipient}, with email {recipient_email}.'
    say(response)

def ask_to_create_contact(recipient, recipient_email):
    response = f'Would you like to create a contact for {recipient} with email address {recipient_email}?'
    say(response)
    user_response = listen()
    return user_response

def get_email_from_user(recipient):
    response = f"I couldn't find a contact for {recipient}, can you tell me their email?"
    say(response)
    user_response = listen()
    return user_response

def get_recipients_from_user():
    response = "Sorry I couldn't find an email recipient, can you tell me who this email is intended for?"
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
    response = 'Try requesting again.'
    say(response)

def prompt_user_to_update_email():
    response = 'Please update your email in your settings to send an email.'
    say(response)

def prompt_user_to_update_app_password():
    response = 'Please update your app password in your settings to send an email.'
    say(response)

def prompt_user_sending_email():
    response = 'Sending your email.'
    say(response)

def prompt_user_showing_email():
    response = "Ok, I'll bring up the email for you to edit."
    say(response)

def ask_to_send_email():
    response = 'Would you Like to send the email?'
    say(response)
    user_response = listen()
    return user_response

def prompt_user_writing_email(recipients):
    recipient_referral = ''
    for recipient in recipients:
        if recipients.index(recipient) == len(recipients) - 1 and recipients.index(recipient) != 0:
            recipient_referral += 'and '
        elif recipients.index(recipient) != 0:
            recipient_referral += ', '
        recipient = recipient.replace('my', 'your')
        recipient_referral += f'{recipient}'
    
    response = f'Writing your email to {recipient_referral}.'
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

def report_weather(city, temperature):
    response = f'The weather in {city} is {temperature} degrees.'
    say(response)
    
def greeting(username):
    hour = datetime.now().hour
    if hour < 12:
        response = 'Good Morning '
    elif hour >= 12 and hour < 18:
        response = 'Good Afternoon '    
    elif hour >= 18 and hour < 21:
        response = 'Good Evening '
    else:
        response = 'Hope your night is well '
    response += username
    say(response)