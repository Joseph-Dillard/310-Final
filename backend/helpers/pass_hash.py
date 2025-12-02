from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def pass_hash(password):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    return hashed_password

def check_pass(hashedpass, password):
    valid_pass = bcrypt.check_password_hash(hashedpass, password)
    return valid_pass