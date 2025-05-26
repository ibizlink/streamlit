from .db import fetch_all_users

def get_authenticator_data():
    users = fetch_all_users()
    credentials = {"usernames": {}}
    for user in users:
        email = user[0]
        hashed_pw = user[1]
        user_id = user[2]
        is_admin = bool(user[3])
        credentials["usernames"][email] = {
            "email": email,
            "name": email.split('@')[0],
            "password": hashed_pw,
            "user_id": user_id,
            "is_admin": is_admin
        }
    return credentials