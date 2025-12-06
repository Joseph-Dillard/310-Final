import threading
import tkinter as tk
from tkinter import ttk, messagebox

import frontend.api_con as api


class ManagerDashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Manager Dashboard", font=(None, 16)).pack(pady=6)
        cols = ("order_no", "user_no", "tot_price", "payment_status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=6)
        ttk.Button(btn_frame, text="Mark Paid", command=self.markpaid).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Add Book", command=self.openaddbook).pack(side="left")
        ttk.Button(btn_frame, text="Manage Books", command=self.openmanagebooks).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Logout", command=self.logout).pack(side="right")

    def update_orders(self, status, data):
        for i in self.tree.get_children():
            self.tree.delete(i)
        if status != 200:
            messagebox.showerror("Error", str(data))
            return
        orders = data.get('All orders') if isinstance(data, dict) else None
        if not orders:
            return
        for o in orders:
            self.tree.insert('', 'end', values=(o.get('order_no'), o.get('user_no'), o.get('tot_price'), o.get('payment_status')))

    def markpaid(self):
        sel = self.tree.selection()
        if not sel:
            return
        order_no = int(self.tree.item(sel[0])['values'][0])
        threading.Thread(target=self.workerupdate, args=(order_no,), daemon=True).start()

    def workerupdate(self, order_no):
        try:
            res = api.manager_update_payment(order_no)
            if res['status_code'] == 200:
                messagebox.showinfo('Updated', 'Payment marked paid')
                ords = api.manager_view_orders()
                self.controller.queue.put(("managerorder", (ords['status_code'], ords['data'])))
            else:
                messagebox.showerror('Error', str(res['data']))
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def openaddbook(self):
        AddBookDialog(self)

    def openmanagebooks(self):
        BookManagerDialog(self)

    def logout(self):
        api.logout()
        self.controller.show_frame("StartPage")


class AddBookDialog(tk.Toplevel):
    def __init__(self, parent: ManagerDashboard):
        super().__init__(parent)
        self.title('Add Book')
        ttk.Label(self, text='Title').pack(); self.title_e = ttk.Entry(self); self.title_e.pack()
        ttk.Label(self, text='Author').pack(); self.author_e = ttk.Entry(self); self.author_e.pack()
        ttk.Label(self, text='Price Buy').pack(); self.buy_e = ttk.Entry(self); self.buy_e.pack()
        ttk.Label(self, text='Price Rent').pack(); self.rent_e = ttk.Entry(self); self.rent_e.pack()
        ttk.Label(self, text='Stock').pack(); self.stock_e = ttk.Entry(self); self.stock_e.pack()
        ttk.Button(self, text='Add', command=self.doadd).pack(pady=6)

    def doadd(self):
        try:
            title = self.title_e.get(); auth = self.author_e.get(); buy = float(self.buy_e.get()); rent = float(self.rent_e.get()); stock = int(self.stock_e.get())
        except Exception as e:
            messagebox.showerror('Input', str(e)); return
        threading.Thread(target=self.worker, args=(title, auth, buy, rent, stock), daemon=True).start()
        self.destroy()

    def worker(self, title, auth, buy, rent, stock):
        try:
            res = api.manager_add_book(title, auth, buy, rent, stock)
            if res['status_code'] in (200, 201):
                messagebox.showinfo('Added', 'Book added')
            else:
                messagebox.showerror('Error', str(res['data']))
        except Exception as e:
            messagebox.showerror('Error', str(e))


class BookManagerDialog(tk.Toplevel):
    def __init__(self, parent: ManagerDashboard):
        super().__init__(parent)
        self.title('Manage Books')
        self.geometry('700x400')
        self.parent = parent
        cols = ('book_no', 'title', 'author', 'price_buy', 'price_rent', 'no_available')
        self.tree = ttk.Treeview(self, columns=cols, show='headings', height=15)
        for c in cols:
            self.tree.heading(c, text=c)
        self.tree.pack(fill='both', expand=True, padx=6, pady=6)
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=6)
        ttk.Button(btn_frame, text='Refresh', command=self.refresh).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Edit Selected', command=self.editselected).pack(side='left', padx=4)
        ttk.Button(btn_frame, text='Close', command=self.destroy).pack(side='right')
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            res = api.search_books("")
            if res['status_code'] != 200:
                messagebox.showerror('Error', str(res['data']))
                return
            books = res['data'].get('book_list') if isinstance(res['data'], dict) else None
            if not books:
                return
            for b in books:
                name = b.get('book_name') or b.get('title')
                no_avail = b.get('no_available')
                if no_avail is None:
                    no_avail = 0
                self.tree.insert('', 'end', values=(b.get('book_no'), name, b.get('author'), b.get('price_buy'), b.get('price_rent'), no_avail))
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def editselected(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])['values']
        EditBookDialog(self, vals)


class EditBookDialog(tk.Toplevel):
    def __init__(self, parent: BookManagerDialog, book_vals):
        super().__init__(parent)
        self.parent = parent
        self.book_no = int(book_vals[0])
        self.title('Edit Book')
        ttk.Label(self, text='Title').pack(); self.title_e = ttk.Entry(self); self.title_e.pack()
        ttk.Label(self, text='Author').pack(); self.author_e = ttk.Entry(self); self.author_e.pack()
        ttk.Label(self, text='Price Buy').pack(); self.buy_e = ttk.Entry(self); self.buy_e.pack()
        ttk.Label(self, text='Price Rent').pack(); self.rent_e = ttk.Entry(self); self.rent_e.pack()
        ttk.Label(self, text='Stock').pack(); self.stock_e = ttk.Entry(self); self.stock_e.pack()
        self.title_e.insert(0, book_vals[1])
        self.author_e.insert(0, book_vals[2])
        self.buy_e.insert(0, book_vals[3])
        self.rent_e.insert(0, book_vals[4])
        self.stock_e.insert(0, book_vals[5] if book_vals[5] is not None else 0)
        ttk.Button(self, text='Save', command=self.dosave).pack(pady=6)

    def dosave(self):
        try:
            title = self.title_e.get(); auth = self.author_e.get(); buy = float(self.buy_e.get()); rent = float(self.rent_e.get()); stock = int(self.stock_e.get())
        except Exception as e:
            messagebox.showerror('Input', str(e)); return
        threading.Thread(target=self.worker, args=(title, auth, buy, rent, stock), daemon=True).start()
        self.destroy()

    def worker(self, title, auth, buy, rent, stock):
        try:
            res = api.manager_update_book(self.book_no, title, auth, buy, rent, stock)
            if res['status_code'] == 200:
                messagebox.showinfo('Updated', 'Book updated')
                self.parent.refresh()
            else:
                messagebox.showerror('Error', str(res['data']))
        except Exception as e:
            messagebox.showerror('Error', str(e))
