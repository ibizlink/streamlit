import bcrypt

def get_hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())