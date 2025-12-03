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
    if token.startswith('Bearer '):
        token = token[7:]
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except ExpiredSignatureError:
        return {"error": "expired session"}
    except InvalidTokenError:
        return {"error": "Invalid token. login again."}
    