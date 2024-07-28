import sys
import json
from classifying_layer.module_layer.email.email_handler import send_email

data = sys.stdin.read()
data_dict = json.loads(data)

module = data_dict["module"]

if module == 'email':
    try:
        send_email(data_dict["email"], data_dict["appPassword"], data_dict["recipient"], data_dict["subject"], data_dict["body"],  data_dict["cc"], data_dict['bcc'])
    except Exception as e:
        print(f'Error occured sending email: {e}')
