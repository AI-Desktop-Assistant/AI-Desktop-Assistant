# necessary imports
from models.load_model import load_model
from classifying_layer.module_layer.response.response import *
from classifying_layer.module_layer.email.writitng_agent import generate_email
from classifying_layer.module_layer.handle_confirmation import get_y_or_n
from classifying_layer.module_layer.email.email_handler import send_email
import sqlite3
import time

email_info_model_path = 'models\\email_info_recognizer.pth'
email_intent_model_path = 'models\\email_intent_recognizer.pth'
email_entity_model_path = 'models\\entity_recognizer.pth'
email_info_model, tokenizer, device = load_model(email_info_model_path, 'email')
email_intent_model, tokenizer, device = load_model(email_intent_model_path, 'email')
email_entity_model, tokenizer, device = load_model(email_entity_model_path, 'email')

current_user_id = ''

def predict_tokens(req, model):
        tokenized_input = tokenizer([req], truncation=True, padding='max_length', is_split_into_words=True, return_tensors="pt")

        input_ids = tokenized_input['input_ids'].to(device)
        attention_mask = tokenized_input['attention_mask'].to(device)
        
        outputs = model(input_ids, attention_mask)

        logits = outputs.logits
        predicted_token_class_ids = logits.argmax(-1)

        tokens = tokenizer.convert_ids_to_tokens(input_ids.squeeze().tolist())

        predicted_tokens_classes = [model.config.id2label[t.item()] for t in predicted_token_class_ids[0]]

        return tokens, predicted_tokens_classes

def format_to_email(response):
    email = ''
    if 'at' not in response:
        return ''
    for word in response.split():
        if word == 'at':
            email += "@"
        else:
            email += word
    return email

def prompt_user_for_email(recipient, attempt=0):
    if attempt == 3:
        return ''
    response = get_email_from_user(recipient)
    email = format_to_email(response)
    if email == '':
        alert_not_understood()
        attempt += 1
        prompt_user_for_email(recipient, attempt)
    return email


def find_unknown_recipients(recipients, cc, bcc, recipients_found, ccs_found, bccs_found):
    found_recipients = []
    found_ccs = []
    found_bccs = []
    for recipient in recipients:
        if recipient not in recipients_found:
            email = prompt_user_for_email(recipient)
            if email == '':
                prompt_user_to_retry()
                return [], [], []
            recipient_email = ''
            for word in email.split():
                if word.endswith('@gmail.com'):
                    recipient_email = word
                    break
            found_recipients.append(recipient_email)
            response = ask_to_create_contact(recipient, recipient_email)
            y_or_n = get_y_or_n(response)
            if y_or_n == 'yes':
                alert_creating_contact(recipient, recipient_email)
                add_contact(recipient, recipient_email)
    for recipient in cc:
        if recipient not in ccs_found:
            email = prompt_user_for_email(recipient)
            if email == '':
                prompt_user_to_retry()
                return [], [], []
            cc_email = ''
            for word in email.split():
                if word.endswith('@gmail.com'):
                    cc_email = word
                    break
            found_ccs.append(cc_email)
            response = ask_to_create_contact(recipient, cc_email)
            y_or_n = get_y_or_n(response)
            if y_or_n == 'yes':
                alert_creating_contact(recipient, cc_email)
                add_contact(recipient, cc_email)
        
    for recipient in bcc:
        if recipient not in bccs_found:
            email = prompt_user_for_email(recipient)
            if email == '':
                prompt_user_to_retry()
                return [], [], []
            bcc_email = ''
            for word in email.split():
                if word.endswith('@gmail.com'):
                    bcc_email = word
                    break
            found_bccs.append(bcc_email)
            response = ask_to_create_contact(recipient, bcc_email)
            y_or_n = get_y_or_n(response)
            if y_or_n == 'yes':
                alert_creating_contact(recipient, bcc_email)
                add_contact(recipient, bcc_email)
    return found_recipients, found_ccs, found_bccs

def add_contact(name, email):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        current_time = time.localtime()
        month = current_time.tm_mon
        day = current_time.tm_mday
        year = current_time.tm_year
        hour = current_time.tm_hour
        minute = current_time.tm_mday
        second = current_time.tm_sec
        timestamp = f'{month}/{day}/{year} {hour}:{minute}:{second}'
        global current_user_id
        print(f'Current User ID: {current_user_id}')
        cursor.execute("INSERT INTO contacts (user_id, contact_name, contact_email, timestamp) VALUES (?, ?, ?, ?)", (current_user_id, name, email, timestamp))

def get_emails_from_contacts(recipient_names, cc_names, bcc_names):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts")
        rows = cursor.fetchall()
        recipient_emails = recipients_found = []
        cc_emails = ccs_found = []
        bcc_emails = bccs_found = []
        
        for row in rows:
            for recipient in recipient_names:
                if recipient in row[2]:
                    recipient_emails.append(row[3])
                    recipients_found.append(recipient)
            for cc in cc_names:
                if cc in row[2]:
                    cc_emails.append(row[3])
                    ccs_found.append(cc)
            for bcc in bcc_names:
                if bcc in row[2]:
                    bcc_emails.append(row[3])
                    bccs_found.append(bcc)
        return recipient_emails, cc_emails, bcc_emails, recipients_found, ccs_found, bccs_found

def get_email_and_app_password(user_id):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id))
        rows = cursor.fetchall()
        row = rows[0]
        email = row[3]
        app_password = row[4]
        return email, app_password

def get_footer():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id=?', (current_user_id))
        rows = cursor.fetchall()
        footer = rows[0][6]
        if footer == '':
            prompt_to_update_footer()
            return ''
        footer = '\n\n' + footer
        return footer

def get_contact_names(recipients, cc, bcc):
    recipient_contact_names = []
    cc_contact_names = []
    bcc_contact_names = []
    for recipient in recipients:
        if not recipient.endswith('@gmail.com'):
            recipient_contact_names.append(recipient)
    if len(cc) > 0:
        for cc_recipient in cc:
            if not cc_recipient.endswith('@gmail.com'):
                cc_contact_names.append(cc_recipient)

    if len(bcc) > 0:
        for bcc_recipient in bcc:
            if not bcc_recipient.endswith('@gmail.com'):
                bcc_contact_names.append(bcc_recipient)
    return recipient_contact_names, cc_contact_names, bcc_contact_names

def group_recipients(recipients, cc, bcc):
    grouped_recipients = []
    grouped_cc = []
    grouped_bcc = []
    recipient = ''
    previous_label = ''
    for recipient_token, label in recipients:
        if previous_label == '':
            recipient += recipient_token
        elif label == previous_label:
            recipient += ' '
            recipient += recipient_token
        else:
            grouped_recipients.append(recipient)
            recipient = recipient_token
        previous_label = label
    if recipient not in grouped_recipients:
        grouped_recipients.append(recipient)


    if len(cc) > 0:
        cc_recipient = ''
        previous_label = ''
        for cc_token, label in cc:
            if previous_label == '':
                cc_recipient += cc_token
            elif label == previous_label:
                cc_recipient += ' '
                cc_recipient += cc_token
            else:
                grouped_cc.append(cc_recipient)
                cc_recipient = cc_token
            previous_label = label

        if cc_recipient not in grouped_cc:
            grouped_cc.append(cc_recipient)
            

    if len(bcc) > 0:
        bcc_recipient = ''
        previous_label = ''
        for bcc_token, label in bcc:
            if previous_label == '':
                bcc_recipient += bcc_token
            elif label == previous_label:
                bcc_recipient += ' '
                bcc_recipient += bcc_token
            else:
                grouped_bcc.append(bcc_recipient)
                bcc_recipient = bcc_token
            previous_label = label
        if bcc_recipient not in grouped_bcc:
            grouped_bcc.append(bcc_recipient)

    return grouped_recipients, grouped_cc, grouped_bcc

def handle_intent_not_sufficient():
    response = get_intent_from_user()
    if response == '':
        response = get_intent_from_user()
        if response == '':
            return ''
    return response

def handle_no_recipients():
    response = get_recipients_from_user()
    if response == '':
        response = get_recipients_from_user()
        if response == '':
            return []
    entities = parse_email_entities(response)
    return entities

def validate_intent(intents):
    intent_sufficient = False
    if len(intents['D-INTENT']) > 0:
        intent_sufficient = True

    # if necessary information is missing get the necessary information from the user
    if not intent_sufficient:
        intents['AddedDetail'] = handle_intent_not_sufficient()
    
    return intents

def validate_recipients(recipients):
    recipients_present = False
    if len(recipients) > 0:
        recipients_present = True
    if not recipients_present:
        recipients = handle_no_recipients()
    
    return recipients

def parse_email_entities(req):
    email_entity_model.eval()
    tokens, predict_tokens_classes = predict_tokens(req, email_entity_model)
    entity_predictions = []
    for token, token_classes in zip(tokens, predict_tokens_classes):
        if token_classes[-1] != '0' and token != '[PAD]' and token != '[CLS]' and token != '[SEP]':
            if token.startswith("##"):
                print(f'')
                entity_predictions[-1] += token[2:]
            else:
                entity_predictions.append(token)
    return entity_predictions

def parse_email_recipients(req):
    email_info_model.eval()
    tokens, predicted_tokens_classes = predict_tokens(req, email_info_model)
    recipient_predictions = []
    cc_predictions = []
    bcc_predictions = []
    predictions = []

    labels_to_index = {'O': 0, '1-REC-ENT': 1, '2-REC-ENT': 2, 'S-1-CC-ENT': 3, '1-CC-ENT': 4, 'S-1-BCC-ENT': 5, '1-BCC-ENT': 6, '2-CC-ENT': 7, '2-BCC-ENT': 8}
    index_to_label = {'0': 'O', '1': '1-REC-ENT', '2': '2-REC-ENT', '3': 'S-1-CC-ENT', '4': '1-CC-ENT', '5': 'S-1-BCC-ENT', '6': '1-BCC-ENT', '7': '2-CC-ENT', '8': '2-BCC-ENT'}
    for token, token_class in zip(tokens, predicted_tokens_classes):
        if token_class[-1] != '0' and token != '[PAD]' and token != '[CLS]' and token != '[SEP]':
            if int(token_class[-1]) == labels_to_index['1-REC-ENT'] or  int(token_class[-1]) == labels_to_index['2-REC-ENT']:
                if token.startswith("##"):
                    try:
                        recipient_predictions[-1][0] += token[2:]
                    except IndexError:
                        predictions[-1][0] = token[2:]
                else:
                    recipient_predictions.append((token, index_to_label[token_class[-1]]))
            elif int(token_class[-1]) == labels_to_index['1-CC-ENT'] or int(token_class[-1]) == labels_to_index['2-CC-ENT']:
                if token.startswith("##"):
                    try:
                        cc_predictions[-1][0] += token[2:]
                    except IndexError:
                        predictions[-1][0] = token[2:]
                else:
                    cc_predictions.append((token, index_to_label[token_class[-1]]))
            elif int(token_class[-1]) == labels_to_index['1-BCC-ENT'] or int(token_class[-1]) == labels_to_index['2-BCC-ENT']:
                if token.startswith("##"):
                    try:
                        print(f'')
                        bcc_predictions[-1][0] += token[2:]
                    except IndexError:
                        predictions[-1][0] = token[2:]
                else:
                    bcc_predictions.append((token, index_to_label[token_class[-1]]))
            else:
                predictions.append((token, index_to_label[token_class[-1]]))
            

    return recipient_predictions, cc_predictions, bcc_predictions

def parse_email_intent(req):
    email_intent_model.eval()
    tokens, predicted_tokens_classes = predict_tokens(req, email_intent_model)
    labels_to_index = {'A-INTENT': '0', 'M-INTENT': '1', 'O': '2', 'T-INTENT': '3', 'S-INTENT': '4', 'D-INTENT': '5', 'W-INTENT': '6'}
    predictions = {'A-INTENT': [], 'M-INTENT': [], 'O': [], 'T-INTENT': [], 'S-INTENT': [], 'D-INTENT': [], 'W-INTENT': []}
    
    for token, token_class in zip(tokens, predicted_tokens_classes):
        if token_class[-1] != labels_to_index['O'] and token != '[PAD]'and token != '[CLS]'and token != '[SEP]':
            if token_class[-1] == labels_to_index['A-INTENT']:
                if token.startswith('##'):
                    predictions["A-INTENT"][-1] += token[2:]
                else: 
                    predictions['A-INTENT'].append(token)
            elif token_class[-1] == labels_to_index['M-INTENT']:
                if token.startswith('##'):
                    predictions["M-INTENT"][-1] += token[2:]
                else: 
                    predictions['M-INTENT'].append(token)
            elif token_class[-1] == labels_to_index['T-INTENT']:
                if token.startswith('##'):
                    predictions["T-INTENT"][-1] += token[2:]
                else: 
                    predictions['T-INTENT'].append(token)
            elif token_class[-1] == labels_to_index['S-INTENT']:
                if token.startswith('##'):
                    predictions["S-INTENT"][-1] += token[2:]
                else: 
                    predictions['S-INTENT'].append(token)
            elif token_class[-1] == labels_to_index['D-INTENT']:
                if token.startswith('##'):
                    predictions["D-INTENT"][-1] += token[2:]
                else: 
                    predictions['D-INTENT'].append(token)
            elif token_class[-1] == labels_to_index['W-INTENT']:
                if token.starts_with('##'):
                    predictions["W-INTENT"][-1] += token[2:]
                else: 
                    predictions['W-INTENT'].append(token)
            else:
                predictions['O'].append(token)
    return predictions
        
def process_email_req(req, user_id):
    global current_user_id
    current_user_id = user_id
    
    # take in email request
    # pass email request to model
    recipients, cc, bcc = parse_email_recipients(req)
    print(f'Recipients: {recipients}\nCC: {cc}\nBCC: {bcc}')
    # analyze if recipients are missing from request
    recipients = validate_recipients(recipients)
    recipients, cc, bcc = group_recipients(recipients, cc, bcc)
    print(f'Recipients: {recipients}\nCC: {cc}\nBCC: {bcc}')
    if len(recipients) == 0:
        return ''
    # analyze if intent is missing from request
    intents = parse_email_intent(req)
    print(f'Intents: {str(intents)}')
    intents = validate_intent(intents)
    if len(intents) == 0:
        return ''
    print(f'Intents: {str(intents)}')
    # Have email writing agent generate a subject and body with no footer
    body, subject = generate_email(req, intents)
    print(f'{body}\n{subject}')
    # Get the users footer
    footer = get_footer()
    if footer == '':
        return ''
    # combine body and footer
    body += footer
    print(body)
    # if user requested an email draft ask if they want to see the email
    if 'send' in intents['A-INTENT']:
        recipient_contact_names, cc_contact_names, bcc_contact_names = get_contact_names(recipients, cc, bcc)
        recipient_emails, cc_emails, bcc_emails, recipients_found, ccs_found, bccs_found = get_emails_from_contacts(recipient_contact_names, cc_contact_names, bcc_contact_names)
        found_recipients, found_ccs, found_bccs = find_unknown_recipients(recipients, cc, bcc, recipients_found, ccs_found, bccs_found)
        recipient_emails.append(found_recipients)
        cc_emails.append(found_ccs)
        bcc_emails.append(found_bccs)
        user_email, app_password = get_email_and_app_password(user_id)
        if user_email == '':
            prompt_user_to_update_email()
            return ''
        send_email(user_email, app_password, recipient_emails, subject, body, cc=cc_emails, bcc=bcc_emails)

        
        

                