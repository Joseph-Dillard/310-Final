import threading
import tkinter as tk
from tkinter import ttk, messagebox

import frontend.api_con as api


class CatalogPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        top = ttk.Frame(self)
        top.pack(fill="x", pady=4)
        ttk.Button(top, text="Logout", command=self.logout).pack(side="right")
        ttk.Button(top, text="View Cart", command=lambda: controller.show_frame("CartPage")).pack(side="right")
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", pady=6)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(search_frame, text="Search", command=self.dosearch).pack(side="left", padx=4)

        cols = ("book_no", "title", "author", "price_buy", "price_rent")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Add as Buy", command=lambda: self.addselected(1)).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Add as Rent", command=lambda: self.addselected(2)).pack(side="left")

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.search_var.set("")
        self.dosearch()

    def logout(self):
        api.logout()
        self.controller.show_frame("StartPage")

    def dosearch(self):
        word = self.search_var.get()
        threading.Thread(target=self.workersearch, args=(word,), daemon=True).start()

    def workersearch(self, word):
        try:
            res = api.search_books(word)
            self.controller.queue.put(("search", (res["status_code"], res["data"])))
        except Exception as e:
            self.controller.queue.put(("search", (0, str(e))))

    def update_results(self, status, data):
        for i in self.tree.get_children():
            self.tree.delete(i)
        if status != 200:
            messagebox.showerror("Search error", str(data))
            return
        books = data.get("book_list") if isinstance(data, dict) else None
        if not books:
            messagebox.showinfo("Search", "No results")
            return
        for b in books:
            self.tree.insert('', 'end', values=(b.get('book_no'), b.get('book_name'), b.get('author'), b.get('price_buy'), b.get('price_rent')))

    def addselected(self, purchase_type: int):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a book first")
            return
        vals = self.tree.item(sel[0])['values']
        book_no = int(vals[0])
        book_name = vals[1]
        price = vals[3] if purchase_type == 1 else vals[4]
        threading.Thread(target=self.workeradd, args=(book_no, purchase_type, (book_no, book_name, purchase_type, price)), daemon=True).start()

    def workeradd(self, book_no, purchase_type, book_tuple):
        try:
            res = api.add_to_order(book_no, purchase_type)
            self.controller.queue.put(("orderadd", (res["status_code"], res["data"], book_tuple)))
        except Exception as e:
            self.controller.queue.put(("orderadd", (0, str(e), book_tuple)))


class CartPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Cart", font=(None, 16)).pack(pady=8)
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=6)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=6)
        ttk.Button(btn_frame, text="Checkout", command=self.docheckout).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Back", command=lambda: controller.show_frame("CatalogPage")).pack(side="left")

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.refresh()

    def refresh(self):
        self.listbox.delete(0, 'end')
        for item in self.controller.cart:
            typ = 'Buy' if item[2] == 1 else 'Rent'
            self.listbox.insert('end', f"{item[1]} - {typ} - {item[3]}")

    def docheckout(self):
        threading.Thread(target=self.workercheckout, daemon=True).start()

    def workercheckout(self):
        try:
            res = api.checkout()
            self.controller.queue.put(("checkout", (res["status_code"], res["data"])))
        except Exception as e:
            self.controller.queue.put(("checkout", (0, str(e))))
