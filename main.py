import os
from reception_layer.speech_rec import listen
from classifying_layer.classify_req import classify_user_request

os.environ['USE_FLASH_ATTENTION'] = '1'

while True:
    # listen for input
    input = listen()
    # after getting input classify the model
    module = classify_user_request(input)
    # delve into selected module deeper
    
    
