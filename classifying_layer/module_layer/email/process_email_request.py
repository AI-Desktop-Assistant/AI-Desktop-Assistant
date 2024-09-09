# necessary imports
from models.load_model import load_model
from classifying_layer.module_layer.response.response import *
from classifying_layer.module_layer.email.writitng_agent import generate_email
from classifying_layer.module_layer.handle_confirmation import get_y_or_n
from classifying_layer.module_layer.email.email_handler import send_email
from user_config import *
from config_socketio import get_app_socket
import sqlite3
import time

email_info_model_path = 'models\\email_info_recognizer.pth'
email_intent_model_path = 'models\\email_intent_recognizer.pth'
email_entity_model_path = 'models\\entity_recognizer.pth'
email_info_model, tokenizer, device = load_model(email_info_model_path, 'email')
email_intent_model, tokenizer, device = load_model(email_intent_model_path, 'email')
email_entity_model, tokenizer, device = load_model(email_entity_model_path, 'email')

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
    if '@' not in response and 'at' not in response:
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

def get_contact_emails(recipients, cc, bcc):
    recipient_contact_names, cc_contact_names, bcc_contact_names = get_contact_names(recipients, cc, bcc)
    print(f'Recipient Contacts: {recipient_contact_names}, CC Contact Names: {cc_contact_names}, BCC: {bcc_contact_names}')
    recipient_emails, cc_emails, bcc_emails, recipients_found, ccs_found, bccs_found = get_emails_from_contacts(recipient_contact_names, cc_contact_names, bcc_contact_names)
    print(f'recipient_emails: {recipient_emails}, cc_emails: {cc_emails}, bcc_emails: {bcc_emails}, recipients_found: {recipients_found}, ccs_found: {ccs_found}, bccs_found: {bccs_found}')
    found_recipients, found_ccs, found_bccs = find_unknown_recipients(recipients, cc, bcc, recipients_found, ccs_found, bccs_found)
    print(f'Found Recipients: {found_recipients}, Found CCs: {ccs_found}, Found BCCs: {bccs_found}')
    if len(found_recipients) > 0:
        print(f'Appending to recipient emails: {found_recipients}')
        recipient_emails.append(found_recipients)
    if len(found_ccs) > 0:    
        print(f'Appending to cc emails: {found_ccs}')
        cc_emails.append(found_ccs)
    if len(found_bccs) > 0:
        print(f'Appending to bcc emails: {bccs_found}')
        bcc_emails.append(found_bccs)
    return recipient_emails, cc_emails, bcc_emails

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
        user_id = get_user_id()
        print(f'Current User ID: {user_id}')
        cursor.execute("INSERT INTO contacts (user_id, contact_name, contact_email, timestamp) VALUES (?, ?, ?, ?)", (user_id, name, email, timestamp))

def get_emails_from_contacts(recipient_names, cc_names, bcc_names):
    print(f'Querying for contacts: Recipient Names: {recipient_names}, CC Names: {cc_names}, BCC Names: {bcc_names}')
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        user_id = get_user_id()
        cursor.execute("SELECT * FROM contacts WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        recipient_emails = []
        recipients_found = []
        cc_emails = []
        ccs_found = []
        bcc_emails = []
        bccs_found = []
        
        for row in rows:
            for recipient in recipient_names:
                if not recipient.endswith('.com'):
                    if recipient in row[2] and len(recipient.strip()) > 0:
                        print(f'Appending to recipient emails: {row[3]}')
                        recipient_emails.append(row[3])
                        print(f'Appending to recipients found: {recipient}')
                        recipients_found.append(recipient)
                        print(f'Recipient Emails: {recipient_emails}')
                        print(f'Recipients Found: {recipients_found}')
                else:
                    print('Ends with .com')
                    print(f'Appending to recipient emails: {recipient}')
                    recipient_emails.append(recipient)
                    print(f'Appending to recipients found: {recipient}')
                    recipients_found.append(recipient)
                    print(f'Recipient Emails: {recipient_emails}')
                    print(f'Recipients Found: {recipients_found}')
            for cc in cc_names:
                if not cc.endswith('.com'):
                    if cc in row[2] and len(recipient.strip()) > 0:
                        print(f'Appending to cc emails: {row[3]}')
                        cc_emails.append(row[3])
                        print(f'Appending to ccs found: {cc}')
                        ccs_found.append(cc)
                        print(f'Recipient Emails: {cc_emails}')
                        print(f'Recipients Found: {ccs_found}')
                else:
                    print('Ends with .com')
                    print(f'Appending to cc emails: {cc}')
                    cc_emails.append(cc)
                    print(f'Appending to ccs found: {cc}')
                    ccs_found.append(cc)
                    print(f'Recipient Emails: {cc_emails}')
                    print(f'Recipients Found: {ccs_found}')
            for bcc in bcc_names:
                if not bcc.endswith('.com'):
                    if bcc in row[2] and len(recipient.strip()) > 0:
                        print(f'Appending to bcc emails: {row[3]}')
                        bcc_emails.append(row[3])
                        print(f'Appending to bccs found: {bcc}')
                        bccs_found.append(bcc)
                        print(f'Recipient Emails: {bcc_emails}')
                        print(f'Recipients Found: {bccs_found}')
                else:
                    print('Ends with .com')
                    print(f'Appending to bcc emails: {bcc}')
                    bcc_emails.append(bcc)
                    print(f'Appending to bccs found: {bcc}')
                    bccs_found.append(bcc)
                    print(f'Recipient Emails: {bcc_emails}')
                    print(f'Recipients Found: {bccs_found}')
        return recipient_emails, cc_emails, bcc_emails, recipients_found, ccs_found, bccs_found

def get_email_and_app_password():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        user_id = get_user_id()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        rows = cursor.fetchall()
        row = rows[0]
        email = row[3]
        app_password = row[4]
        return email, app_password

def get_footer():
    print('Getting Footer')
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        user_id = get_user_id()
        cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
        rows = cursor.fetchall()
        footer = rows[0][6]
        if footer == '':
            return ''
        footer = '\n\n' + footer
        return footer

def get_contact_names(recipients, cc, bcc):
    recipient_contact_names = []
    cc_contact_names = []
    bcc_contact_names = []
    for recipient in recipients:
        if not recipient.endswith('.com'):
            recipient_contact_names.append(recipient)
    if len(cc) > 0:
        for cc_recipient in cc:
            if not cc_recipient.endswith('.com'):
                cc_contact_names.append(cc_recipient)

    if len(bcc) > 0:
        for bcc_recipient in bcc:
            if not bcc_recipient.endswith('.com'):
                bcc_contact_names.append(bcc_recipient)
    print(f'Got Contacts: {recipient_contact_names}, {cc_contact_names}, {bcc_contact_names}')
    return recipient_contact_names, cc_contact_names, bcc_contact_names

def group_recipients(recipients, cc, bcc):
    print(f'Recipients to group: Recipients: {recipients}, CC: {cc}, BCC: {bcc}')
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
    print(f'Grouped Recipients: {grouped_recipients}')

    if len(cc) > 0:
        print(f'Grouping CCs: {cc}')
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
        print(f'Grouped CCs: {grouped_cc}')

    if len(bcc) > 0:
        print(f'Grouping BCC: {bcc}')
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
        print(f'Grouped BCCs: {grouped_bcc}')
    return grouped_recipients, grouped_cc, grouped_bcc

def handle_intent_not_sufficient():
    response = get_intent_from_user()
    if response == 'Sorry, I didn\'t understand your request':
        response = get_intent_from_user()
        if response == 'Sorry, I didn\'t understand your request':
            return ''
    return response

def handle_no_recipients():
    print(f'Getting Recipient from User')
    response = get_recipients_from_user()
    if response == 'Sorry, I didn\'t understand your request':
        print(f'Getting Recipient from User')
        response = get_recipients_from_user()
        if response == 'Sorry, I didn\'t understand your request':
            return []
    entities = parse_email_entities(response)
    print(f'Entity predictions: {entities}')
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
    print(f'Recipients to Validate: {recipients}')
    recipients_present = False
    if len(recipients) > 0:
        recipients_present = True
    if not recipients_present:
        print('No Recipients Found')
        recipients = handle_no_recipients()
    return recipients

def parse_email_entities(req):
    print(f'Parsing email Entities')
    try:
        email_entity_model.eval()
        print(f'predicting tokens')
        tokens, predict_tokens_classes = predict_tokens(req, email_entity_model)
        print(f'Predicted Tokens And Classes: Tokens: {tokens}, Predicted Token Classes: {predict_tokens_classes}')
        entity_predictions = []
        for token, token_class in zip(tokens, predict_tokens_classes):
            if token_class[-1] != '0' and token != '[PAD]' and token != '[CLS]' and token != '[SEP]':
                print(f'Token: {token}, Token Class Entity: {token_class}')
                if token.startswith("##"):
                    entity_predictions[-1] += token[2:]
                else:
                    entity_predictions.append((token, token_class))
    except Exception as e:
        print(e)

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

def substitute_recipients(body, recipients):
    recipient_referral = 'Dear '
    for recipient in recipients:
        if recipients.index(recipient) == len(recipients) - 1 and recipients.index(recipient) != 0:
            recipient_referral += 'and '
        elif recipients.index(recipient) != 0:
            recipient_referral += ', '
        recipient_referral += f'{recipient.capitalize()}'
    print(f'Recipients referral: {recipient_referral}')
    split_body = body.split('\n')
    split_body[0] = f'{recipient_referral},'
    new_body = '\n'.join(split_body)
    print(f'Substituted Body: {new_body}')
    return new_body
    

def process_email_req(req):
    # take in email request
    # pass email request to model
    print('Getting Email Recipients')
    recipients, cc, bcc = parse_email_recipients(req)
    print(f'Recipients: {recipients}\nCC: {cc}\nBCC: {bcc}')
    # analyze if recipients are missing from request
    print('Validating Recipients')
    recipients = validate_recipients(recipients)
    print(f'Validated Recipients: {recipients}')
    print(f'Grouping Recipients')
    recipients, cc, bcc = group_recipients(recipients, cc, bcc)
    print(f'Recipients: {recipients}\nCC: {cc}\nBCC: {bcc}')
    if len(recipients) == 0:
        print('No Recipients Found')
        return ''
    # analyze if intent is missing from request
    print('Parsing Email Intent')
    intents = parse_email_intent(req)
    print(f'Intents: {str(intents)}')
    print('Validating intent')
    intents = validate_intent(intents)
    if len(intents) == 0:
        print('intent not found')
        return ''
    print(f'Intents: {str(intents)}')
    prompt_user_writing_email(recipients)
    # Have email writing agent generate a subject and body with no footer    
    print('Generating email')
    body, subject = generate_email(req, intents)
    print(f'Generated Body and Subject\nBody: {body}\nSubject: {subject}')
    # Get the users footer
    print('Getting user footer')
    footer = get_footer()
    print(f'Footer: {footer}')
    if footer == '':
        print('No Footer Found')
        prompt_to_update_footer()
        return ''
    print(f'Substituting Recipient Name: {recipients}')
    body = substitute_recipients(body, recipients)
    print(f'Substituted Body: {body}')
    # combine body and footer
    print(f'Combining body and footer')
    body += footer
    print(f'Body + Footer: {body}')
    # if user requested an email draft ask if they want to see the email
    print('Getting Contacts')
    recipient_emails, cc_emails, bcc_emails = get_contact_emails(recipients, cc, bcc)
    print(f'Recipient Emails: {recipient_emails}')
    print(f'CC Emails: {cc_emails}')
    print(f'BCC Emails: {bcc_emails}')
    if 'send' in intents['A-INTENT']:
        user_email, app_password = get_email_and_app_password()
        if user_email == '':
            prompt_user_to_update_email()
            return ''
        if app_password == '':
            prompt_user_to_update_app_password()
            return ''
        response = ask_to_show_email()
        y_or_n = get_y_or_n(response)
        if y_or_n == 'yes':
            respond_showing_email()
            data = {'body': body, 'subject': subject, 'recipients': recipient_emails, 'cc': cc_emails, 'bcc': bcc_emails}
            socket = get_app_socket()[1]
            socket.emit('response', { 'purpose': 'show-email', 'data': data })
        else:
            response = ask_to_send_email()
            y_or_n = get_y_or_n(response)
            if y_or_n == 'yes':
                prompt_user_sending_email()
                send_email(user_email, app_password, recipient_emails, subject, body, cc=cc_emails, bcc=bcc_emails)
            else:
                prompt_user_showing_email()
                data = {'body': body, 'subject': subject, 'recipients': recipient_emails, 'cc': cc_emails, 'bcc': bcc_emails}
                socket = get_app_socket()[1]
                socket.emit('response', { 'purpose': 'show-email', 'data': data })
    else:
        response = ask_to_show_email()
        y_or_n = get_y_or_n(response)
        if y_or_n == 'yes':
            respond_showing_email()
            data = {'body': body, 'subject': subject, 'recipients': recipient_emails, 'cc': cc_emails, 'bcc': bcc_emails}
            socket = get_app_socket()[1]
            socket.emit('response', { 'purpose': 'show-email', 'data': data })
        else:
            respond_ending_request_chain()
            return ''
