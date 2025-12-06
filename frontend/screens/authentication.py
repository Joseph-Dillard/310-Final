import threading
import tkinter as tk
from tkinter import ttk, messagebox

import frontend.api_con as api


def add_placeholder(entry: ttk.Entry, placeholder: str, is_password: bool = False):
    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, 'end')
            if is_password:
                entry.config(show='*')

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder)
            if is_password:
                entry.config(show='')

    entry.insert(0, placeholder)
    if is_password:
        entry.config(show='')
    entry.bind('<FocusIn>', on_focus_in)
    entry.bind('<FocusOut>', on_focus_out)


class UserLoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="User Login", font=(None, 16)).pack(pady=10)
        self.username = ttk.Entry(self)
        self.username.pack(pady=5)
        add_placeholder(self.username, "username")
        self.password = ttk.Entry(self, show="*")
        self.password.pack(pady=5)
        add_placeholder(self.password, "password", is_password=True)
        ttk.Button(self, text="Login", command=self.dologin).pack(pady=5)
        ttk.Button(self, text="Back", command=lambda: controller.show_frame("StartPage")).pack()

    def dologin(self):
        u = self.username.get()
        p = self.password.get()
        threading.Thread(target=self.worker, args=(u, p), daemon=True).start()

    def worker(self, u, p):
        try:
            res = api.login(u, p)
            self.controller.queue.put(("login", (res["status_code"], res["data"])))
        except Exception as e:
            self.controller.queue.put(("login", (0, str(e))))


class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Register", font=(None, 16)).pack(pady=10)
        ttk.Label(self, text="Username:").pack(anchor="w", padx=20)
        self.username = ttk.Entry(self)
        self.username.pack(pady=5, padx=20, fill="x")
        add_placeholder(self.username, "username")
        ttk.Label(self, text="Email:").pack(anchor="w", padx=20)
        self.email = ttk.Entry(self)
        self.email.pack(pady=5, padx=20, fill="x")
        add_placeholder(self.email, "email")
        ttk.Label(self, text="Password:").pack(anchor="w", padx=20)
        self.password = ttk.Entry(self, show="*")
        self.password.pack(pady=5, padx=20, fill="x")
        add_placeholder(self.password, "password", is_password=True)
        ttk.Button(self, text="Create Account", command=self.doregister).pack(pady=5)
        ttk.Button(self, text="Back", command=lambda: controller.show_frame("StartPage")).pack()

    def doregister(self):
        u = self.username.get(); e = self.email.get(); p = self.password.get()
        threading.Thread(target=self.worker, args=(u, e, p), daemon=True).start()

    def worker(self, u, e, p):
        try:
            res = api.register(u, e, p)
            self.controller.queue.put(("register", (res["status_code"], res["data"])))
        except Exception as ex:
            self.controller.queue.put(("register", (0, str(ex))))


class ManagerLoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Manager Login", font=(None, 16)).pack(pady=10)
        self.username = ttk.Entry(self)
        self.username.pack(pady=5)
        add_placeholder(self.username, "username")
        self.password = ttk.Entry(self, show="*")
        self.password.pack(pady=5)
        add_placeholder(self.password, "password", is_password=True)
        ttk.Button(self, text="Login", command=self.dologin).pack(pady=5)
        ttk.Button(self, text="Back", command=lambda: controller.show_frame("StartPage")).pack()

    def dologin(self):
        u = self.username.get(); p = self.password.get()
        threading.Thread(target=self.worker, args=(u, p), daemon=True).start()

    def worker(self, u, p):
        try:
            res = api.manager_login(u, p)
            if res['status_code'] == 200:
                self.controller.queue.put(("login", (200, res['data'])))
                ords = api.manager_view_orders()
                self.controller.queue.put(("managerorder", (ords['status_code'], ords['data'])))
                self.controller.show_frame("ManagerDashboard")
            else:
                self.controller.queue.put(("login", (res['status_code'], res['data'])))
        except Exception as e:
            self.controller.queue.put(("login", (0, str(e))))

    
