from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from backend import dbcon, models, helpers

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
