from email.message import EmailMessage
import ssl
import smtplib

def send_email(sender, password, recipients, subject, body, attatchments = [], cc=[], bcc=[]):
    # Should be a standardized footer input by the user
    footer = ''

    em = EmailMessage()
    em['From'] = sender
    em['To'] = recipients
    em['Subject'] = subject
    if len(cc) != 0:
        em['Cc'] = cc
    if len(bcc) != 0:
        em['Bcc'] = bcc
    em.set_content(body + footer)
    if len(attatchments) > 0:
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

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, recipients, em.as_string())
