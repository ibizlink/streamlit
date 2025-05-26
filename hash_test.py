import bcrypt

password = "TraMe3ef@"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print(hashed.decode())