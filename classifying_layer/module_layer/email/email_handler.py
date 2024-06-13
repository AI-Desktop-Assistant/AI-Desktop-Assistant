from email.message import EmailMessage
import ssl
import smtplib

# Currently only able to work with gmail
email_sender = 'aidangonzalez648@gmail.com'

# Not the password associated with user name
# This is an "app password" that can be created at myaccount.google.com/apppasswords
email_password = 'wocoiehkzzincsew'

# Will be either retrieved or inputted by the user
email_reciever = 'aidangonzalezwork@gmail.com'

subject = 'Testing python email script'

body = """
This is a test email body for this email
"""
# Should be a standardized footer input by the user
footer = ''

em = EmailMessage()
em['From'] = email_sender
em['To'] = email_reciever
em['Subject'] = subject
em.set_content(body + footer)

context = ssl.create_default_context()

with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_reciever, em.as_string())
