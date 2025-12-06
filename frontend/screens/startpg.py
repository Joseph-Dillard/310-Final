import tkinter as tk
from tkinter import ttk


class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Welcome to CS 310 Final Bookstore App", font=(None, 20)).pack(pady=20)
        ttk.Button(self, text="User Login", command=lambda: controller.show_frame("UserLoginPage")).pack(pady=5)
        ttk.Button(self, text="Register", command=lambda: controller.show_frame("RegisterPage")).pack(pady=5)
        ttk.Button(self, text="Manager Login", command=lambda: controller.show_frame("ManagerLoginPage")).pack(pady=5)
