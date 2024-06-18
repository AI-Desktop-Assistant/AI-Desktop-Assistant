import sys
import json
from classifying_layer.module_layer.email.email_handler import send_email

data = sys.stdin.read()
data_dict = json.loads(data)

module = data_dict["module"]

if module == 'email':
    send_email(data_dict["sender"], data_dict["password"], data_dict["recipients"], data_dict["cc"], data_dict["subject"], data_dict["body"])