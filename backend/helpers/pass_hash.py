from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def pass_hash(password: str):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    return hashed_password