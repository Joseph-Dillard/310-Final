from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from backend import dbcon, models, helpers

app = Flask(__name__)

@app.route('/order_create_add', methods=['POST'])
def create_add_order():
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
            return jsonify({'error': 'No JWT'}), 401
        
        tok_data = helpers.JWT_auth.tok_ver(token)
        if tok_data == "Session expired. login again." or tok_data == "Invalid token. login again.":
            return jsonify({'error': tok_data}), 401
        user_no = tok_data['user_no']
        current_order = db.query(models.orders).filter_by(user_no=user_no).first()
        if not current_order:
            return jsonify({'error': 'Cart is empty'}), 400

        for book in db.query(models.order_details).filter_by(order_no=current_order.order_no).all():
            total_price += book.price
        current_order.tot_price = total_price
        current_order.payment_status = 1
        db.commit()
        return jsonify({'message': 'Order completed!', 'total_price': str(total_price)}), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        helpers.email_helper.send_order_email(user.email, current_order.order_no, total_price)
        db.close()






