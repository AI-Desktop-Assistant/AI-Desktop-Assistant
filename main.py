import os
import sys
from flask import Flask, request, jsonify
from threading import Thread
from reception_layer.speech_rec import listen
from classifying_layer.classify_req import classify_user_request

os.environ['USE_FLASH_ATTENTION'] = '1'
logged_in = True
current_user_id = ''
current_username = ''
current_email = ''

app = Flask(__name__)

def run_flask():
    app.run(port=5000, debug=False)

def main_loop(user_id, username, email):
    global current_user_id
    global current_username
    global current_email

    current_user_id = user_id
    current_username = username
    current_email = email
    print('Starting Main Loop')
    while True:
        if logged_in:
            # listen for input
            try:
                input = listen()
            except:
                continue
            # input = "Compose an update email to the customer service team and CC the support manager and quality assurance lead and BCC the technical support lead and IT manager"
            # after getting input classify the model
            module = classify_user_request(input, current_user_id)
            # delve into selected module deeper

@app.route('/update_email', methods=['POST'])
def update_username():
    print('updating username')
    global current_username
    new_username = request.json.get('username')
    if new_username:
        print('updated email')
        current_username = new_username
        return jsonify(success=True, message="Username updated successfully!")
    return jsonify(success=False, message="Unable to update username in main.py")

@app.route('/update_username', methods=['POST'])
def update_email():
    print('updating email')
    global current_email
    new_email = request.json.get('email')
    if new_email:
        print('updated email')
        current_email = new_email
        return jsonify(success=True, message="Email updated successfully!")
    return jsonify(success=False, message="Unable to update email in main.py")

@app.route('/login', methods=['POST'])
def update_login_status():
    print('updating login status')
    global logged_in
    login_status = request.json.get('login')
    if login_status:
        logged_in = login_status
        print('updated Login status')
        return jsonify(success=True, message="Login status updated successfully!")
    return jsonify(success=False, message="Unable to update login_status in main.py")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python main.py <user_id> <username> <email>")
        sys.exit(1)
    current_user_id = sys.argv[1]
    current_username = sys.argv[2]
    current_email = sys.argv[3]
    print(f'User ID: {current_user_id}, Username: {current_username}, Email: {current_email}')
    print("\nStarting flask\n")
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    main_loop(current_user_id, current_username, current_email)