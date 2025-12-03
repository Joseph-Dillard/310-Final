from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from backend import dbcon, models, helpers

app = Flask(__name__)

@app.route('/registeruser', methods=['POST'])
def register_user():
    logindata = request.get_json() or {}
    username = logindata.get('username')
    if (not username):
        return jsonify({'error': 'Username is empty'}), 400
    email = logindata.get('email')
    if (not email) or ('@' not in email):
        return jsonify({'error': 'Invalid email address. Must contain @'}), 400
    password = logindata.get('password')
    if (not password):
        return jsonify({'error': 'Password is empty'}), 400
    password = helpers.pass_hash.pass_hash(password)
    user_insert = models.Users(username=username, email=email, password=password)
    try:
        db = next(dbcon.db_con())
        db.add(user_insert)
        db.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/loginuser', methods=['POST'])
def login():
    logindata = request.get_json()
    username = logindata.get('username')
    password = logindata.get('password')
    if (not username) or (not password):
        return jsonify({'error': 'Username or password is empty'}), 400

    try:
        db = next(dbcon.db_con())
        user = db.query(models.Users).filter_by(username=username).first()
        if not user and not helpers.pass_hash.check_pass(user.password, password):
            return jsonify({'message': 'Invalid login'}), 401
        else if user and helpers.pass_hash.check_pass(user.password, password):
            token = helpers.JWT_auth.token_gen(user.user_no)
            return jsonify({'message': 'Login successful', 'token': token,'user': {'id': user.user_no, 'username': user.username}}), 200
        else:
            return jsonify({'error': 'Invalid login'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
