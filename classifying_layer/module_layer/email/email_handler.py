from email.message import EmailMessage
import ssl
import smtplib
import sqlite3
from config_socketio import get_app_socket
from user_config import get_user_id
from datetime import datetime

def insert_sent_email(subject, body, recipients, cc, timestamp):
    if isinstance(recipients, list):
        recipients_str = ', '.join(recipients)
    else:
        recipients_str = recipients
    if isinstance(cc, list):
        cc_str = ', '.join(cc)
    else:
        cc_str = cc
    with sqlite3.connect('users.db') as conn:
        query = 'INSERT INTO sent_emails (user_id, subject, body, recipient, cc, timestamp) VALUES (?, ?, ?, ?, ?, ?)' 
        user_id = get_user_id()
        conn.execute(query, (user_id, subject, body, recipients_str, cc_str, timestamp))
        conn.commit()

def send_email(sender, password, recipients, subject, body, attatchments=[], cc=[], bcc=[]):
    # Should be a standardized footer input by the user
    print(f'Subject: {subject}')
    print(f'Body: {body}')
    print(f'Sender: {sender}')
    print(f'Recipients: {recipients}')
    print(f'CC: {cc}')
    print(f'BCC: {bcc}')
    print(f'Attatchments: {attatchments}')
    em = EmailMessage()
    em['From'] = sender
    em['To'] = recipients
    em['Subject'] = subject
    if len(cc) != 0:
        em['Cc'] = cc
    if len(bcc) != 0:
        em['Bcc'] = bcc
    em.set_content(body)
    if len(attatchments) > 0:
        print('Adding attatchments to email')
        mime_map = { 'jpg': ('image', 'jpeg'), 'png': ('image', 'png'), 'gif': ('application', 'gif'), 'txt': ('text', 'plain'), 'html': ('text', 'html'), 'doc': ('application', 'msword'), 'docx': ('application', 'vnd.openxmlformats-officedocument.wordprocessingml.document'), 'other': ('application', 'octet-stream') }
        for attatchment in attatchments:
            with open(attatchment, 'rb') as f:
                file_data = f.read()
                file_name = f.name
                ext = file_name.split('.')[-1]
            try:
                maintype, subtype = mime_map[ext]
            except KeyError:
                maintype, subtype = mime_map['other']
            em.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)
    context = ssl.create_default_context()
    print(f'Email: {em}')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            print('Logging in')
            smtp.login(sender, password)
            print(f'Sending email: Sender: {sender}, Recipients: {recipients}, Email: {em}')
            smtp.sendmail(sender, recipients, em.as_string())
        timestamp = datetime.now()
        insert_sent_email(subject, body, recipients, cc, timestamp)
        socket = get_app_socket()[1]
        socket.emit('response', {'purpose': 'sent-email', 'recipients': recipients, 'cc': cc, 'bcc': bcc, 'subject': subject, 'body': body})
    except Exception as e:
        print(e)