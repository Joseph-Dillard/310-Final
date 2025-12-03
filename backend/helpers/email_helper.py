import smtplib, ssl

def send_email(receiver_email,order_no,price,book_list):
    port = 465  # For SSL

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("310pythonemail@gmail.com", "310finalpython")
        
        sender_email = "310pythonemail@gmail.com"
        message = f"Congratulations! You have successfully placed an order!\nOrder No: {order_no}\nTotal Price: {price}\nBooks: {', '.join(book_list)}"
        server.sendmail(sender_email, receiver_email, message)
    return True
