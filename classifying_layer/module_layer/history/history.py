from config_socketio import get_app_socket

response_user = ''
command_user = ''

def user_response(response):
    print(f"The response for history is...........: {response}")
    global response_user
    response_user = response_user + response
    return

def user_command(command):
    socket = get_app_socket()[1]
    print(f"The command for history is............: {command}")
    global command_user
    global response_user
    if command_user == '':
        response_user = ''
        command_user = command
        print(f"If statement: {command_user}")
    else:
        socket.emit('response', {'purpose': 'command-user', 'historyCommand': command_user, 'historyResponse': response_user, 'success': True})
        print(f"Emit from user_command: {command_user},{response_user}")
        command_user = command
        response_user = ''
    return