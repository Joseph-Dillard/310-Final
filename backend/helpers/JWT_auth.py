import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

secret = 'secretkey'

def token_gen(user_no):
    payload = {
        'user_no': user_no,
    }
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token

def tok_ver(token):
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except ExpiredSignatureError:
        return "Session expired. login again."
    except InvalidTokenError:
        return "Invalid token. login again."
    