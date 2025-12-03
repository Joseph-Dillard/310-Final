from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from backend import dbcon, models, helpers

app = Flask(__name__)

@app.route('/book_search', methods=['GET'])
def book_search():
    db = next(dbcon.db_con())

    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No JWT'}), 401
        
        tok_data = helpers.JWT_auth.tok_ver(token)
        if tok_data == "Session expired. login again." or tok_data == "Invalid token. login again.":
            return jsonify({'error': tok_data}), 401
        
        user_no = tok_data['user_no']
        user = db.query(models.Users).filter_by(user_no=user_no).first()
        word = request.args.get('word', '')
        if not word:
            return jsonify({'error': 'No search word provided'}), 400
        
        book_list = db.query(models.books).filter(models.books.title.like(f'%{word}%')).all()
        author_book_list = db.query(models.books).filter(models.books.author.like(f'%{word}%')).all()

        book_list_preap = []
        author_book_list_preap = []
        final_book_list = []

        for i in book_list:
            book_list_preap.append({
                'book_id': i.book_id,
                'title': i.title,
                'author': i.author,
                'price_buy': i.price,
                'price_rent': i.stock
            })
        for j in author_book_list:
            author_book_list_preap.append({
                'book_id': j.book_id,
                'title': j.title,
                'author': j.author,
                'price_buy': j.price,
                'price_rent': j.stock
            })
        for i in author_book_list_preap:
            if i not in book_list_preap:
                final_book_list.append(i)

        return jsonify({'book_list': final_book_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()