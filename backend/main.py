import os
from flask import Flask, jsonify, request
from flask_cors import CORS

from backend import dbcon, models, helpers

app = Flask(__name__)
app.config["ENV"] = os.getenv("FLASK_ENV", "development")
app.config["DEBUG"] = app.config["ENV"] == "development"
app.config["FRONTEND_ORIGIN"] = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

CORS(app, supports_credentials=True, origins=app.config["FRONTEND_ORIGIN"])

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
    user_insert = models.users(username=username, email=email, password=password)
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
        user = db.query(models.users).filter_by(username=username).first()
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



@app.route('/books/search', methods=['GET'])
def book_search():
    db = next(dbcon.db_con())

    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token for authorization'}), 401
        
        tok_data = helpers.JWT_auth.tok_ver(token)
        if tok_data == "Session expired. login again." or tok_data == "Invalid token. login again.":
            return jsonify({'error': tok_data}), 401
        
        user_no = tok_data['user_no']
        user = db.query(models.users).filter_by(user_no=user_no).first()
        word = request.args.get('word', '')
        if not word:
            return jsonify({'error': 'No search word provided'}), 400
        
        book_list = db.query(models.books).filter(models.books.book_name.like(f'%{word}%')).all()
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


@app.route('/orders/create_add', methods=['POST'])
def create_add_order():
    db = next(dbcon.db_con())

    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token for authorization'}), 401
        
        tok_data = helpers.JWT_auth.tok_ver(token)
        if tok_data == "Session expired. login again." or tok_data == "Invalid token. login again.":
            return jsonify({'error': tok_data}), 401
        
        user_no = tok_data['user_no']
        user = db.query(models.users).filter_by(user_no=user_no).first()
        bookdata = request.get_json() or {}
        book_no = bookdata.get('book_no')
        purchase_type = bookdata.get('purchase_type')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    try:
        current_order = db.query(models.orders).filter_by(user_no=user_no).first()
        if not current_order:
            new_order = models.orders(user_no=user_no)
            db.add(new_order)
            db.commit()
            order_no = new_order.order_no
        else:
            order_no = current_order.order_no
        book_quantity = db.query(models.books).filter_by(book_no=book_no).first()
        no_available = book_quantity.no_available
        if no_available <= 0:
            return jsonify({'error': 'Book out of stock'}), 400
        if purchase_type == 1:
            price = book_quantity.price_buy
        elif purchase_type == 2:
            price = book_quantity.price_rent
    
        order_details_insert = db.add(models.order_details(order_no=order_no, book_no=book_no, purchase_type=purchase_type, price=price))
        book_quantity.no_available = no_available - 1
        db.commit()
        return jsonify({'message': 'Order detail added successfully', 'order_no': order_no}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/orders/checkout', methods=['POST'])
def order_checkout():
    db = next(dbcon.db_con())
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token for authorization'}), 401
        
        tok_data = helpers.JWT_auth.tok_ver(token)
        if tok_data == "Session expired. login again." or tok_data == "Invalid token. login again.":
            return jsonify({'error': tok_data}), 401
        user_no = tok_data['user_no']
        current_order = db.query(models.orders).filter_by(user_no=user_no).first()
        if not current_order:
            return jsonify({'error': 'Cart is empty'}), 400

        book_list = []
        total_price = 0
        for book in db.query(models.order_details).filter_by(order_no=current_order.order_no).all():
            title = db.query(models.books).filter_by(book_no=book.book_no).first().title
            book_list.append(title)
            total_price += book.price
        current_order.tot_price = total_price
        current_order.payment_status = 1
        db.commit()
        return jsonify({'message': 'Order completed!', 'total_price': str(total_price)}), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        helpers.email_helper.send_email(user.email, current_order.order_no, total_price, book_list)
        db.close()


@app.route('/manager/login', methods=['POST'])
def manager_login():
    logindata = request.get_json() or {}
    username = logindata.get('username')
    password = logindata.get('password')
    if (not username) or (not password):
        return jsonify({'error': 'Username or password is empty'}), 400

    try:
        db = next(dbcon.db_con())
        manager = db.query(models.users).filter_by(username=username).first()
        if not manager or not helpers.pass_hash.check_pass(manager.password, password):
            return jsonify({'message': 'Invalid login'}), 401
        if manager.role != 1:
            return jsonify({'error': 'Unauthorized access. Managers only!'}), 403
        token = helpers.JWT_auth.token_gen(manager.user_no)
        return jsonify({'message': 'Login successful', 'token': token, 'manager': {'id': manager.user_no, 'username': manager.username}}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/manager/view_orders', methods=['GET'])
def view_all_orders():
    db = next(dbcon.db_con())
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token for authorization'}), 401
        
        tok_data = helpers.JWT_auth.tok_ver(token)
        if tok_data == "Session expired. login again." or tok_data == "Invalid token. login again.":
            return jsonify({'error': tok_data}), 401
        
        manager_no = tok_data['user_no']
        manager = db.query(models.users).filter_by(user_no=manager_no).first()
        if manager.role != 1:
            return jsonify({'error': 'Unauthorized access'}), 403

        orders = db.query(models.orders).all()
        all_orders = []
        for order in orders:
            if order.status == 1:
                status_str = 'Buy'
            else:
                status_str = 'Rent'
            if order.payment_status == 1:
                payment_status_str = 'Pending'
            else:
                payment_status_str = 'Paid'
            all_orders.append({
                'order_no': order.order_no,
                'user_no': order.user_no,
                'status': status_str,
                'tot_price': str(order.tot_price),
                'payment_status': payment_status_str
            })
        return jsonify({'All orders': all_orders}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/manager/update_payment', methods=['POST'])
def update_payment():
    db = next(dbcon.db_con())
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token for authorization'}), 401
        
        tok_data = helpers.JWT_auth.tok_ver(token)
        if tok_data == "Session expired. login again." or tok_data == "Invalid token. login again.":
            return jsonify({'error': tok_data}), 401
        
        manager_no = tok_data['user_no']
        manager = db.query(models.users).filter_by(user_no=manager_no).first()
        if manager.role != 1:
            return jsonify({'error': 'Not a manager!'}), 403

        data = request.get_json() or {}
        order_no = data.get('order_no')
        if not order_no:
            return jsonify({'error': 'Must provide order number'}), 400

        order = db.query(models.orders).filter_by(order_no=order_no).first()
        if not order:
            return jsonify({'error': 'Order does not exist'}), 404

        order.payment_status = 2
        db.commit()
        return jsonify({'message': 'Payment status updated to Paid'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
    
@app.route('/manager/add_new_book', methods=['POST'])
def add_new_book():
    db = next(dbcon.db_con())
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token for authorization'}), 401
        
        tok_data = helpers.JWT_auth.tok_ver(token)
        if tok_data == "Session expired. login again." or tok_data == "Invalid token. login again.":
            return jsonify({'error': tok_data}), 401
        
        manager_no = tok_data['user_no']
        manager = db.query(models.users).filter_by(user_no=manager_no).first()
        if manager.role != 1:
            return jsonify({'error': 'Not a manager!'}), 403

        bookdata = request.get_json() or {}
        title = bookdata.get('title')
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        author = bookdata.get('author')
        if not author:
            return jsonify({'error': 'Author is required'}), 400
        price_buy = bookdata.get('price_buy')
        if price_buy is None:
            return jsonify({'error': 'Buy price is required'}), 400
        price_rent = bookdata.get('price_rent')
        if price_rent is None:
            return jsonify({'error': 'Rent price is required'}), 400
        stock = bookdata.get('stock')
        if stock is None:
            return jsonify({'error': 'Stock is required'}), 400

        new_book = models.books(title=title, author=author, price_buy=price_buy, price_rent=price_rent, stock=stock, no_available=stock)
        db.add(new_book)
        db.commit()
        return jsonify({'message': 'New book added successfully', 'book_no': new_book.book_no}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/manager/update_books', methods=['POST'])
def update_book_info():
    db = next(dbcon.db_con())
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token for authorization'}), 401
        
        tok_data = helpers.JWT_auth.tok_ver(token)
        if tok_data == "Session expired. login again." or tok_data == "Invalid token. login again.":
            return jsonify({'error': tok_data}), 401
        
        manager_no = tok_data['user_no']
        manager = db.query(models.users).filter_by(user_no=manager_no).first()
        if manager.role != 1:
            return jsonify({'error': 'Not a manager!'}), 403

        bookdata = request.get_json() or {}
        book_no = bookdata.get('book_no')
        if not book_no:
            return jsonify({'error': 'Book number is required'}), 400

        book = db.query(models.books).filter_by(book_no=book_no).first()
        if not book:
            return jsonify({'error': 'Book does not exist'}), 404

        title = bookdata.get('title')
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        author = bookdata.get('author')
        if not author:
            return jsonify({'error': 'Author is required'}), 400
        price_buy = bookdata.get('price_buy')
        if price_buy is None:
            return jsonify({'error': 'Buy price is required'}), 400
        price_rent = bookdata.get('price_rent')
        if price_rent is None:
            return jsonify({'error': 'Rent price is required'}), 400
        stock = bookdata.get('stock')
        if stock is None:
            return jsonify({'error': 'Stock is required'}), 400

        book.title = title
        book.author = author
        book.price_buy = price_buy
        book.price_rent = price_rent
        book.no_available = stock

        db.commit()
        return jsonify({'message': 'Book information updated successfully'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
