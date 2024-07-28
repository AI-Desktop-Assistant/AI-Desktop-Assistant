user_id = ''
user_email = ''
username = ''

def configure_user(id, email, name):
    set_user_id(id)
    set_user_email(email)
    set_username(name)

def get_user():
    print(f'Getting user: {user_id}, {user_email}, {username}')
    return user_id, user_email, username

def get_user_id():
    print(f'Getting user id: {user_id}')
    return user_id

def get_user_email():
    print(f'Getting email: {user_email}')
    return user_email

def get_username():
    print(f'Getting username: {username}')
    return username

def set_user_id(id):
    global user_id
    user_id = id
    print(f'Setting User ID: {user_id}')

def set_user_email(email):
    global user_email
    user_email = email
    print(f'Setting Email: {user_email}')

def set_username(name):
    global username
    username = name
    print(f'Setting Username: {username}')