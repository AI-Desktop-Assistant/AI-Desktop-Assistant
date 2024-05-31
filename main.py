from reception_layer.speech_rec import listen
from reception_layer.classifying_layer.classify_req import classify_user_request
from reception_layer.classifying_layer.module_layer.launch.process_launch_req import process_launch_req

while True:
    # listen for input
    input = listen()
    # after getting input classify the model
    module = classify_user_request(input)
    # delve into selected module deeper
    if module == 'launch':
        status = process_launch_req(input)
    # elif module == 'weather':
    #     weather(input)
    # elif module == 'email':
    #     email(input)
    # elif module == 'task':
    #     task(input)
    # elif module == 'spotify':
    #     spotify(input)
    # elif module == 'generic':
    #     generic(input)
    
