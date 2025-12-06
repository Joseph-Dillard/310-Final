import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox

from .startpg import StartPage
from .authentication import UserLoginPage, RegisterPage, ManagerLoginPage
from .bookcatalog import CatalogPage, CartPage
from .manscreen import ManagerDashboard


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bookstore Client")
        self.geometry("800x500")
        self.queue = queue.Queue()

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for sinlge in (StartPage, UserLoginPage, RegisterPage, CatalogPage, CartPage, ManagerLoginPage, ManagerDashboard):
            page_name = sinlge.__name__
            frame = sinlge(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.cart = [] 

        self.show_frame("StartPage")
        self.after(100, self.processqueue)

    def processqueue(self):
        try:
            while True:
                tag, payload = self.queue.get_nowait()
                handler_name = f"handle{tag}"
                if hasattr(self, handler_name):
                    getattr(self, handler_name)(payload)
        except queue.Empty:
            pass
        self.after(100, self.processqueue)
    
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def handlesearch(self, payload):
        frame: CatalogPage = self.frames["CatalogPage"]
        status, data = payload
        frame.update_results(status, data)

    def handlelogin(self, payload):
        status, data = payload
        if status == 200:
            messagebox.showinfo("Login", "Login successful")
            if isinstance(data, dict) and "manager" in data:
                self.show_frame("ManagerDashboard")
            else:
                self.show_frame("CatalogPage")
        else:
            messagebox.showerror("Login failed", str(data))

    def handleregister(self, payload):
        status, data = payload
        if status == 201:
            messagebox.showinfo("Register", "Account created. Please login.")
            self.show_frame("UserLoginPage")
        else:
            messagebox.showerror("Register failed", str(data))

    def handleorderadd(self, payload):
        status, data, book = payload
        if status in (200, 201):
            messagebox.showinfo("Cart", f"Added to order: {book[1]}")
            self.cart.append(book)
        else:
            messagebox.showerror("Add failed", str(data))

    def handlecheckout(self, payload):
        status, data = payload
        if status == 200:
            messagebox.showinfo("Checkout", f"Order completed. Total: {data.get('total_price', 'N/A')}")
            self.cart.clear()
            self.show_frame("CatalogPage")
        else:
            messagebox.showerror("Checkout failed", str(data))

    def handlemanagerorder(self, payload):
        status, data = payload
        frame: ManagerDashboard = self.frames["ManagerDashboard"]
        frame.update_orders(status, data)
