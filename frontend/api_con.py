import requests

BASE_URL = "http://127.0.0.1:5000"

_token = None


def set_token(token):
	global _token
	_token = token


def get_headers():
	headers = {"Content-Type": "application/json"}
	if _token:
		headers["Authorization"] = _token
	return headers


def register(username: str, email: str, password: str):
	url = BASE_URL + "/registeruser"
	payload = {"username": username, "email": email, "password": password}
	resp = requests.post(url, json=payload, headers=get_headers())
	try:
		data = resp.json()
	except ValueError:
		data = {"raw": resp.text}
	return {"status_code": resp.status_code, "data": data}


def login(username: str, password: str):
	url = BASE_URL + "/loginuser"
	payload = {"username": username, "password": password}
	resp = requests.post(url, json=payload, timeout=10)
	try:
		data = resp.json()
	except ValueError:
		data = {"raw": resp.text}
	if resp.status_code == 200 and isinstance(data, dict) and "token" in data:
		set_token(data["token"])
	return {"status_code": resp.status_code, "data": data}


def manager_login(username: str, password: str):
	url = BASE_URL + "/manager/login"
	payload = {"username": username, "password": password}
	resp = requests.post(url, json=payload, timeout=10)
	try:
		data = resp.json()
	except ValueError:
		data = {"raw": resp.text}
	if resp.status_code == 200 and isinstance(data, dict) and "token" in data:
		set_token(data["token"])
	return {"status_code": resp.status_code, "data": data}


def search_books(word: str, timeout: int = 10):
	url = f"{BASE_URL}/books/search"
	payload = {"word": word}
	resp = requests.get(url, params=payload, headers=get_headers(), timeout=timeout)
	try:
		data = resp.json()
	except ValueError:
		data = {"raw": resp.text}
	return {"status_code": resp.status_code, "data": data}


def add_to_order(book_no: int, purchase_type: int, timeout: int = 10):
	url = f"{BASE_URL}/orders/create_add"
	payload = {"book_no": book_no, "purchase_type": purchase_type}
	resp = requests.post(url, json=payload, headers=get_headers(), timeout=timeout)
	try:
		data = resp.json()
	except ValueError:
		data = {"raw": resp.text}
	return {"status_code": resp.status_code, "data": data}


def checkout(timeout: int = 10):
	url = f"{BASE_URL}/orders/checkout"
	resp = requests.post(url, headers=get_headers(), timeout=timeout)
	try:
		data = resp.json()
	except ValueError:
		data = {"raw": resp.text}
	return {"status_code": resp.status_code, "data": data}


def manager_view_orders(timeout: int = 10):
	url = f"{BASE_URL}/manager/view_orders"
	resp = requests.get(url, headers=get_headers(), timeout=timeout)
	try:
		data = resp.json()
	except ValueError:
		data = {"raw": resp.text}
	return {"status_code": resp.status_code, "data": data}


def manager_update_payment(order_no: int, timeout: int = 10):
	url = f"{BASE_URL}/manager/update_payment"
	payload = {"order_no": order_no}
	resp = requests.post(url, json=payload, headers=get_headers(), timeout=timeout)
	try:
		data = resp.json()
	except ValueError:
		data = {"raw": resp.text}
	return {"status_code": resp.status_code, "data": data}


def manager_add_book(book_name: str, author: str, price_buy: float, price_rent: float, no_available: int, timeout: int = 10):
	url = f"{BASE_URL}/manager/add_new_book"
	payload = {"book_name": book_name, "author": author, "price_buy": price_buy, "price_rent": price_rent, "no_available": no_available}
	resp = requests.post(url, json=payload, headers=get_headers(), timeout=timeout)
	try:
		data = resp.json()
	except ValueError:
		data = {"raw": resp.text}
	return {"status_code": resp.status_code, "data": data}



def manager_update_book(book_no: int, book_name: str, author: str, price_buy: float, price_rent: float, no_available: int, timeout: int = 10):
	url = f"{BASE_URL}/manager/update_books"
	payload = {"book_no": book_no, "book_name": book_name, "author": author, "price_buy": price_buy, "price_rent": price_rent, "no_available": no_available}
	resp = requests.post(url, json=payload, headers=get_headers(), timeout=timeout)
	try:
		data = resp.json()
	except ValueError:
		data = {"raw": resp.text}
	return {"status_code": resp.status_code, "data": data}


def logout():
	set_token(None)

