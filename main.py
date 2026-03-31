import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import csv
import json
import os
from datetime import datetime

# ─────────────────────────────────────────────
#  THEME CONSTANTS
# ─────────────────────────────────────────────
C = {
    "bg":          "#f5f0dc",
    "green_dark":  "#1a5c1a",
    "green_mid":   "#2d7a2d",
    "green_light": "#4caf50",
    "yellow":      "#f5c518",
    "white":       "#ffffff",
    "text":        "#1a1a1a",
    "muted":       "#666666",
    "border":      "#cccccc",
    "blue":        "#1565c0",
    "teal":        "#00897b",
    "orange":      "#e65100",
    "red":         "#c62828",
    "row_alt":     "#faf8f0",
    "row_hover":   "#eef7ee",
    "header_row":  "#f0f0f0",
    "khata_red":   "#ffebee",
    "khata_green": "#e8f5e9",
    "purple":      "#6a1b9a",
}

FONT       = ("Segoe UI", 10)
FONT_BOLD  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SM    = ("Segoe UI", 9)

DATA_FILE = "shop_data.json"

SAMPLE_INVENTORY = [
    {"id": 1,  "name": "Hammer",        "code": "H001",  "price": 10.99, "stock": 50,  "category": "Tools"},
    {"id": 2,  "name": "Screwdriver",   "code": "S002",  "price": 5.49,  "stock": 100, "category": "Tools"},
    {"id": 3,  "name": "Nail Box 1kg",  "code": "N003",  "price": 2.99,  "stock": 200, "category": "Fasteners"},
    {"id": 4,  "name": "Pliers",        "code": "P004",  "price": 15.99, "stock": 30,  "category": "Tools"},
    {"id": 5,  "name": "Tape Measure",  "code": "T005",  "price": 8.99,  "stock": 40,  "category": "Measuring"},
    {"id": 6,  "name": "Drill Bit Set", "code": "D006",  "price": 19.99, "stock": 25,  "category": "Power Tools"},
    {"id": 7,  "name": "Wrench",        "code": "W007",  "price": 12.49, "stock": 35,  "category": "Tools"},
    {"id": 8,  "name": "Paint Brush",   "code": "PB008", "price": 3.99,  "stock": 80,  "category": "Painting"},
    {"id": 9,  "name": "Ladder 6ft",    "code": "L009",  "price": 49.99, "stock": 10,  "category": "Safety"},
    {"id": 10, "name": "Bolt Set",      "code": "B010",  "price": 4.99,  "stock": 150, "category": "Fasteners"},
]

CATEGORIES    = ["All", "Tools", "Fasteners", "Measuring", "Power Tools", "Painting", "Safety"]
PRICE_HISTORY = {}


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def rounded_button(parent, text, command, bg, fg="#ffffff", padx=14, pady=6, font=FONT_BOLD):
    return tk.Button(parent, text=text, command=command, bg=bg, fg=fg, font=font,
                     relief="flat", cursor="hand2", padx=padx, pady=pady,
                     activebackground=bg, activeforeground=fg, bd=0)


# ─────────────────────────────────────────────
#  BASE MODAL
# ─────────────────────────────────────────────
class BaseModal(tk.Toplevel):
    def __init__(self, parent, title, width=460, height=420):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=C["white"])
        self.resizable(False, False)
        self.grab_set()
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()  - width)  // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def header(self, text, color=None):
        color = color or C["green_dark"]
        frm = tk.Frame(self, bg=color)
        frm.pack(fill="x")
        tk.Label(frm, text=text, bg=color, fg=C["white"],
                 font=FONT_BOLD, padx=18, pady=12).pack(side="left")
        return frm

    def body_frame(self):
        frm = tk.Frame(self, bg=C["white"], padx=20, pady=14)
        frm.pack(fill="both", expand=True)
        return frm

    def footer(self):
        frm = tk.Frame(self, bg=C["bg"], pady=10, padx=20)
        frm.pack(fill="x", side="bottom")
        return frm

    def field(self, parent, label, row, default=""):
        tk.Label(parent, text=label, bg=C["white"], fg=C["muted"],
                 font=FONT_SM, anchor="w").grid(row=row, column=0, sticky="w", pady=(8, 1))
        var = tk.StringVar(value=str(default))
        ent = tk.Entry(parent, textvariable=var, font=FONT, relief="solid", bd=1,
                       bg=C["white"], fg=C["text"])
        ent.grid(row=row + 1, column=0, sticky="ew", ipady=5)
        return var, ent

    def dropdown(self, parent, label, row, options, default=""):
        tk.Label(parent, text=label, bg=C["white"], fg=C["muted"],
                 font=FONT_SM, anchor="w").grid(row=row, column=0, sticky="w", pady=(8, 1))
        var = tk.StringVar(value=default)
        cb  = ttk.Combobox(parent, textvariable=var, values=options, state="readonly", font=FONT)
        cb.grid(row=row + 1, column=0, sticky="ew", ipady=4)
        return var


# ─────────────────────────────────────────────
#  ITEM MODAL
# ─────────────────────────────────────────────
class ItemModal(BaseModal):
    def __init__(self, parent, callback, item=None):
        super().__init__(parent, "Edit Item" if item else "Add New Item", 440, 500)
        self.callback = callback
        self.header(f"{'✏  Edit' if item else '➕  Add'} Item")
        body = self.body_frame()
        body.columnconfigure(0, weight=1)
        v = item or {}
        self.v_name,  _ = self.field(body, "Item Name  (نام)",    0, v.get("name", ""))
        self.v_code,  _ = self.field(body, "Item Code  (کوڈ)",    2, v.get("code", ""))
        self.v_price, _ = self.field(body, "Price (Rs.)  (قیمت)", 4, v.get("price", ""))
        self.v_stock, _ = self.field(body, "Stock  (اسٹاک)",      6, v.get("stock", ""))
        self.v_cat = self.dropdown(body, "Category  (زمرہ)", 8,
                                   [c for c in CATEGORIES if c != "All"], v.get("category", "Tools"))
        ft = self.footer()
        rounded_button(ft, "Cancel", self.destroy, C["muted"]).pack(side="right", padx=(6, 0))
        rounded_button(ft, "Save  ✔", self._save, C["green_dark"]).pack(side="right")

    def _save(self):
        name = self.v_name.get().strip()
        code = self.v_code.get().strip()
        if not name or not code:
            messagebox.showerror("Error", "Name and Code are required.")
            return
        try:
            price = float(self.v_price.get())
            stock = int(self.v_stock.get())
            assert price >= 0 and stock >= 0
        except Exception:
            messagebox.showerror("Error", "Price must be a positive number. Stock must be a positive integer.")
            return
        self.callback({"name": name, "code": code, "price": price,
                       "stock": stock, "category": self.v_cat.get()})
        self.destroy()


# ─────────────────────────────────────────────
#  CUSTOMER MODAL  (with credit limit)
# ─────────────────────────────────────────────
class CustomerModal(BaseModal):
    def __init__(self, parent, callback, customer=None):
        super().__init__(parent, "Edit Customer" if customer else "Add New Customer", 440, 440)
        self.callback = callback
        self.header(f"{'✏  Edit' if customer else '➕  Add'} Customer")
        body = self.body_frame()
        body.columnconfigure(0, weight=1)
        v = customer or {}
        self.v_name,    _ = self.field(body, "Customer Name  (نام)",  0, v.get("name", ""))
        self.v_contact, _ = self.field(body, "Contact  (رابطہ)",      2, v.get("contact", ""))
        self.v_address, _ = self.field(body, "Address  (پتہ)",        4, v.get("address", ""))
        tk.Label(body, text="Credit Limit  (ادھار حد)  —  0 = no limit",
                 bg=C["white"], fg=C["muted"], font=FONT_SM, anchor="w"
                 ).grid(row=6, column=0, sticky="w", pady=(8, 1))
        self.v_limit = tk.StringVar(value=str(v.get("credit_limit", 0)))
        tk.Entry(body, textvariable=self.v_limit, font=FONT, relief="solid", bd=1,
                 bg=C["white"], fg=C["text"]).grid(row=7, column=0, sticky="ew", ipady=5)
        ft = self.footer()
        rounded_button(ft, "Cancel", self.destroy, C["muted"]).pack(side="right", padx=(6, 0))
        rounded_button(ft, "Save  ✔", self._save, C["green_dark"]).pack(side="right")

    def _save(self):
        name    = self.v_name.get().strip()
        contact = self.v_contact.get().strip()
        if not name or not contact:
            messagebox.showerror("Error", "Name and Contact are required.")
            return
        try:
            limit = float(self.v_limit.get())
            assert limit >= 0
        except Exception:
            messagebox.showerror("Error", "Credit limit must be 0 or a positive number.")
            return
        self.callback({"name": name, "contact": contact,
                       "address": self.v_address.get().strip(),
                       "credit_limit": limit})
        self.destroy()


# ─────────────────────────────────────────────
#  BILLING MODAL  (Cash / Credit)
# ─────────────────────────────────────────────
class BillingModal(BaseModal):
    def __init__(self, parent, inventory, customers, add_txn_cb, get_balance_cb):
        super().__init__(parent, "Create Bill  بل بنائیں", 650, 610)
        self.inventory      = inventory
        self.customers      = customers
        self.add_txn_cb     = add_txn_cb
        self.get_balance_cb = get_balance_cb
        self.cart           = []

        self.header("  Billing  بلنگ")
        body = tk.Frame(self, bg=C["white"], padx=16, pady=8)
        body.pack(fill="both", expand=True)

        # Customer
        rf = tk.Frame(body, bg=C["white"])
        rf.pack(fill="x", pady=(0, 4))
        tk.Label(rf, text="Customer:", bg=C["white"], font=FONT_BOLD).grid(row=0, column=0, sticky="w")
        self.customer_var  = tk.StringVar(value="Walk-in Customer")
        cnames = ["Walk-in Customer"] + [f"{c['name']} ({c['contact']})" for c in customers]
        self.customer_cb   = ttk.Combobox(rf, textvariable=self.customer_var,
                                          values=cnames, state="readonly", width=36, font=FONT)
        self.customer_cb.grid(row=0, column=1, padx=8)
        self.customer_cb.bind("<<ComboboxSelected>>", self._on_customer_change)
        rf.columnconfigure(1, weight=1)

        self.balance_lbl = tk.Label(body, text="", bg=C["white"], font=FONT_SM, fg=C["red"], anchor="w")
        self.balance_lbl.pack(fill="x", pady=(0, 4))

        # Payment type
        pf = tk.Frame(body, bg=C["white"])
        pf.pack(fill="x", pady=(0, 6))
        tk.Label(pf, text="Payment:", bg=C["white"], font=FONT_BOLD).pack(side="left")
        self.payment_var = tk.StringVar(value="Cash")
        for val, lbl in [("Cash", "💵  Cash  نقد"), ("Credit", "📒  Credit / ادھار")]:
            tk.Radiobutton(pf, text=lbl, variable=self.payment_var, value=val,
                           bg=C["white"], font=FONT, activebackground=C["white"],
                           command=self._on_payment_change).pack(side="left", padx=12)

        # Paid amount row
        self.paid_row = tk.Frame(body, bg=C["white"])
        self.paid_row.pack(fill="x", pady=(0, 6))
        tk.Label(self.paid_row, text="Amount Paid (Rs.):", bg=C["white"], font=FONT_BOLD).pack(side="left")
        self.paid_var = tk.StringVar(value="0")
        tk.Entry(self.paid_row, textvariable=self.paid_var, width=12,
                 font=FONT, relief="solid", bd=1).pack(side="left", padx=8, ipady=4)
        tk.Label(self.paid_row, text="(0 = fully paid)", bg=C["white"],
                 fg=C["muted"], font=FONT_SM).pack(side="left")

        # Item row
        sf = tk.Frame(body, bg=C["white"])
        sf.pack(fill="x", pady=(0, 6))
        tk.Label(sf, text="Item:", bg=C["white"], font=FONT_BOLD).grid(row=0, column=0, sticky="w")
        self.item_var = tk.StringVar()
        inames = [f"{i['name']} ({i['code']})" for i in inventory]
        self.item_cb  = ttk.Combobox(sf, textvariable=self.item_var, values=inames,
                                     state="readonly", width=28, font=FONT)
        self.item_cb.grid(row=0, column=1, padx=8)
        tk.Label(sf, text="Qty:", bg=C["white"], font=FONT_BOLD).grid(row=0, column=2)
        self.qty_var = tk.StringVar(value="1")
        tk.Entry(sf, textvariable=self.qty_var, width=5, font=FONT,
                 relief="solid", bd=1).grid(row=0, column=3, padx=8)
        rounded_button(sf, "Add  ➕", self._add_to_cart, C["green_dark"],
                       padx=10, pady=4).grid(row=0, column=4)

        # Cart
        cols = ("Item", "Code", "Unit Price", "Qty", "Subtotal")
        self.cart_tree = ttk.Treeview(body, columns=cols, show="headings", height=7)
        for col, w in zip(cols, [160, 70, 90, 50, 90]):
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=w, anchor="center")
        self.cart_tree.pack(fill="both", expand=True, pady=4)
        rounded_button(body, "Remove Selected", self._remove_item, C["red"],
                       padx=10, pady=3).pack(anchor="e")

        self.total_var = tk.StringVar(value="Total: Rs. 0.00")
        tk.Label(body, textvariable=self.total_var, bg=C["white"],
                 font=("Segoe UI", 13, "bold"), fg=C["green_dark"]).pack(pady=(4, 0))

        ft = self.footer()
        rounded_button(ft, "Cancel", self.destroy, C["muted"]).pack(side="right", padx=(6, 0))
        rounded_button(ft, "Save Bill  ✔", self._finalize, C["green_dark"]).pack(side="right")

    def _on_customer_change(self, *_):
        sel = self.customer_var.get()
        if sel == "Walk-in Customer":
            self.balance_lbl.config(text="")
            return
        for c in self.customers:
            if f"{c['name']} ({c['contact']})" == sel:
                bal = self.get_balance_cb(c["id"])
                lim = c.get("credit_limit", 0)
                if bal > 0:
                    lt  = f"  |  Limit: Rs. {lim:,.2f}" if lim > 0 else ""
                    self.balance_lbl.config(
                        text=f"⚠  Outstanding Khata: Rs. {bal:,.2f}{lt}", fg=C["red"])
                else:
                    self.balance_lbl.config(text="✔  No outstanding balance", fg=C["teal"])
                break

    def _on_payment_change(self):
        if self.payment_var.get() == "Credit":
            self.paid_row.pack_forget()
        else:
            self.paid_row.pack(fill="x", pady=(0, 6))

    def _add_to_cart(self):
        sel = self.item_var.get()
        if not sel:
            messagebox.showwarning("Select Item", "Please select an item.")
            return
        try:
            qty = int(self.qty_var.get())
            assert qty > 0
        except Exception:
            messagebox.showerror("Error", "Enter a valid quantity.")
            return
        idx  = self.item_cb["values"].index(sel)
        item = self.inventory[idx]
        if qty > item["stock"]:
            messagebox.showerror("Insufficient Stock", f"Only {item['stock']} units available.")
            return
        sub = round(item["price"] * qty, 2)
        self.cart.append({"item": item, "qty": qty, "subtotal": sub})
        self.cart_tree.insert("", "end", values=(item["name"], item["code"],
                                                  f"Rs. {item['price']:.2f}", qty,
                                                  f"Rs. {sub:.2f}"))
        self._update_total()

    def _remove_item(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx = self.cart_tree.index(sel[0])
        self.cart_tree.delete(sel[0])
        self.cart.pop(idx)
        self._update_total()

    def _update_total(self):
        total = sum(e["subtotal"] for e in self.cart)
        self.total_var.set(f"Total: Rs. {total:.2f}")
        if self.payment_var.get() == "Cash":
            self.paid_var.set(f"{total:.2f}")

    def _finalize(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add items first.")
            return
        total   = sum(e["subtotal"] for e in self.cart)
        payment = self.payment_var.get()

        # Resolve customer
        customer_id  = None
        cust_display = self.customer_var.get()
        if cust_display != "Walk-in Customer":
            for c in self.customers:
                if f"{c['name']} ({c['contact']})" == cust_display:
                    customer_id = c["id"]
                    break

        # Credit-only guard
        if payment == "Credit":
            if customer_id is None:
                messagebox.showerror("Error", "Select a registered customer for credit sales.")
                return
            cust = next((c for c in self.customers if c["id"] == customer_id), None)
            if cust:
                lim = cust.get("credit_limit", 0)
                if lim > 0:
                    cur_bal = self.get_balance_cb(customer_id)
                    if cur_bal + total > lim:
                        messagebox.showerror(
                            "Credit Limit Exceeded",
                            f"Limit: Rs. {lim:,.2f}\n"
                            f"Current balance: Rs. {cur_bal:,.2f}\n"
                            f"This bill: Rs. {total:,.2f}\n"
                            f"Total would be: Rs. {cur_bal + total:,.2f}")
                        return
            paid = 0.0
        else:
            try:
                paid = float(self.paid_var.get())
                assert paid >= 0
            except Exception:
                messagebox.showerror("Error", "Enter a valid paid amount.")
                return
            if paid == 0:
                paid = total

        self.add_txn_cb(self.cart, total, customer_id, payment, paid)
        remaining = round(total - paid, 2)
        msg = f"Bill saved!\nTotal: Rs. {total:.2f}\nPaid: Rs. {paid:.2f}"
        if remaining > 0:
            msg += f"\nKhata Added: Rs. {remaining:.2f}"
        messagebox.showinfo("Bill Saved  بل محفوظ", msg)
        self.destroy()


# ─────────────────────────────────────────────
#  KHATA LEDGER MODAL
# ─────────────────────────────────────────────
class KhataModal(tk.Toplevel):
    def __init__(self, parent, customer, transactions, payments, record_payment_cb):
        super().__init__(parent)
        self.title(f"Khata  —  {customer['name']}")
        self.configure(bg=C["white"])
        self.geometry("800x580")
        self.resizable(True, True)
        self.grab_set()

        self.customer          = customer
        self.transactions      = transactions
        self.payments          = payments
        self.record_payment_cb = record_payment_cb

        # Header
        hdr = tk.Frame(self, bg=C["purple"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"📒  Khata  —  {customer['name']}  |  {customer['contact']}",
                 bg=C["purple"], fg=C["white"], font=FONT_BOLD, padx=16, pady=12).pack(side="left")

        # Summary strip
        self.summary_frm = tk.Frame(self, bg=C["bg"])
        self.summary_frm.pack(fill="x", padx=14, pady=(10, 0))

        # Tabs
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=8)

        # Ledger tab
        self.ledger_frm = tk.Frame(nb, bg=C["white"])
        nb.add(self.ledger_frm, text="📋  Ledger  لیجر")
        lcols = ("Date", "Type", "Description", "Debit  ادھار", "Credit  واپسی", "Balance  بقایا")
        self.ledger_tree = ttk.Treeview(self.ledger_frm, columns=lcols, show="headings", height=13)
        for col, w in zip(lcols, [110, 70, 260, 100, 100, 110]):
            self.ledger_tree.heading(col, text=col)
            self.ledger_tree.column(col, width=w, anchor="center")
        lvsb = ttk.Scrollbar(self.ledger_frm, orient="vertical", command=self.ledger_tree.yview)
        self.ledger_tree.configure(yscrollcommand=lvsb.set)
        self.ledger_tree.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        lvsb.pack(side="right", fill="y", pady=6)
        self.ledger_tree.tag_configure("debit",  background=C["khata_red"])
        self.ledger_tree.tag_configure("credit", background=C["khata_green"])

        # Payments tab
        self.pay_frm = tk.Frame(nb, bg=C["white"])
        nb.add(self.pay_frm, text="💵  Payments  ادائیگیاں")
        pcols = ("Date", "Amount Rs.", "Note", "Recorded By")
        self.pay_tree = ttk.Treeview(self.pay_frm, columns=pcols, show="headings", height=13)
        for col, w in zip(pcols, [130, 130, 280, 130]):
            self.pay_tree.heading(col, text=col)
            self.pay_tree.column(col, width=w, anchor="center")
        pvsb = ttk.Scrollbar(self.pay_frm, orient="vertical", command=self.pay_tree.yview)
        self.pay_tree.configure(yscrollcommand=pvsb.set)
        self.pay_tree.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        pvsb.pack(side="right", fill="y", pady=6)

        # Footer — record payment
        foot = tk.Frame(self, bg=C["bg"], pady=10, padx=14)
        foot.pack(fill="x", side="bottom")
        tk.Label(foot, text="Record Payment  ادائیگی درج کریں:",
                 bg=C["bg"], font=FONT_BOLD).pack(side="left")
        self.pay_amount_var = tk.StringVar()
        tk.Entry(foot, textvariable=self.pay_amount_var, width=12,
                 font=FONT, relief="solid", bd=1).pack(side="left", padx=8, ipady=4)
        tk.Label(foot, text="Note:", bg=C["bg"], font=FONT_SM).pack(side="left")
        self.pay_note_var = tk.StringVar()
        tk.Entry(foot, textvariable=self.pay_note_var, width=22,
                 font=FONT, relief="solid", bd=1).pack(side="left", padx=6, ipady=4)
        rounded_button(foot, "✔  Save Payment",
                       self._save_payment, C["green_dark"], padx=10, pady=5).pack(side="left", padx=8)
        rounded_button(foot, "Close", self.destroy, C["muted"], padx=10, pady=5).pack(side="right")

        self._refresh()

    def _refresh(self):
        cid = self.customer["id"]

        # Build sorted entries
        entries = []
        for t in self.transactions:
            if t.get("customer_id") != cid:
                continue
            debit = round(t["total"] - t.get("paid", t["total"]), 2)
            entries.append({"date": t["date"], "type": "Sale",
                             "desc": t.get("items", ""),
                             "debit": debit, "credit": 0.0})
        for p in self.payments:
            if p.get("customer_id") != cid:
                continue
            entries.append({"date": p["date"], "type": "Payment",
                             "desc": p.get("note", ""),
                             "debit": 0.0, "credit": p["amount"]})
        entries.sort(key=lambda x: x["date"])

        self.ledger_tree.delete(*self.ledger_tree.get_children())
        running = 0.0
        for e in entries:
            running = round(running + e["debit"] - e["credit"], 2)
            tag  = "debit" if e["debit"] > 0 else "credit"
            desc = e["desc"][:45] + "…" if len(e["desc"]) > 45 else e["desc"]
            self.ledger_tree.insert("", "end", tags=(tag,), values=(
                e["date"], e["type"], desc,
                f"Rs. {e['debit']:.2f}"  if e["debit"]  > 0 else "—",
                f"Rs. {e['credit']:.2f}" if e["credit"] > 0 else "—",
                f"Rs. {running:.2f}",
            ))

        self.pay_tree.delete(*self.pay_tree.get_children())
        for p in reversed([p for p in self.payments if p.get("customer_id") == cid]):
            self.pay_tree.insert("", "end", values=(
                p["date"], f"Rs. {p['amount']:.2f}", p.get("note", ""), p.get("by", "Owner")))

        # Summary cards
        for w in self.summary_frm.winfo_children():
            w.destroy()
        billed    = sum(t["total"] for t in self.transactions if t.get("customer_id") == cid)
        paid_in   = sum(t.get("paid", t["total"]) for t in self.transactions if t.get("customer_id") == cid)
        payments_ = sum(p["amount"] for p in self.payments if p.get("customer_id") == cid)
        outstanding = round(billed - paid_in - payments_, 2)
        lim  = self.customer.get("credit_limit", 0)
        avail = max(0, lim - outstanding) if lim > 0 else None

        cards = [
            ("Total Billed",      f"Rs. {billed:,.2f}",              C["blue"]),
            ("Total Received",    f"Rs. {paid_in + payments_:,.2f}", C["teal"]),
            ("Outstanding ادھار", f"Rs. {outstanding:,.2f}",
             C["red"] if outstanding > 0 else C["green_dark"]),
        ]
        if avail is not None:
            cards.append(("Credit Available", f"Rs. {avail:,.2f}", C["orange"]))
        for lbl, val, col in cards:
            kf = tk.Frame(self.summary_frm, bg=col, padx=16, pady=8)
            kf.pack(side="left", expand=True, fill="x", padx=4)
            tk.Label(kf, text=lbl, bg=col, fg=C["white"], font=FONT_SM).pack()
            tk.Label(kf, text=val, bg=col, fg=C["white"],
                     font=("Segoe UI", 12, "bold")).pack()

    def _save_payment(self):
        try:
            amount = float(self.pay_amount_var.get())
            assert amount > 0
        except Exception:
            messagebox.showerror("Error", "Enter a valid amount greater than 0.")
            return
        self.record_payment_cb(self.customer["id"], amount, self.pay_note_var.get().strip())
        self.pay_amount_var.set("")
        self.pay_note_var.set("")
        self._refresh()
        messagebox.showinfo("Payment Recorded", f"Rs. {amount:.2f} recorded for {self.customer['name']}")


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class HardwareShopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hardware Shop Management System  |  پارڈویٹر دکان انتظام نظام")
        self.geometry("1280x760")
        self.minsize(960, 620)
        self.configure(bg=C["bg"])
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._load_data()

        self._sort_col = None
        self._sort_rev = False
        self.tree                   = None
        self.customer_tree          = None
        self.txn_tree               = None
        self.txn_customer_filter_cb = None
        self.khata_tree             = None

        self._build_ui()
        self._refresh_table()
        self._refresh_customers_table()
        self._refresh_transactions()
        self._refresh_transactions_customer_filter_cb()
        self._refresh_reports()
        self._refresh_khata_tab()

    # ── PERSISTENCE ───────────────────────────
    def _on_closing(self):
        if messagebox.askokcancel("Quit", "Quit and save?"):
            self._save_data()
            self.destroy()

    def _load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    d = json.load(f)
                self.inventory           = d.get("inventory", [dict(i) for i in SAMPLE_INVENTORY])
                self.transactions        = d.get("transactions", [])
                self.customers           = d.get("customers", [])
                self.price_history       = d.get("price_history", {})
                self.khata_payments      = d.get("khata_payments", [])
                self.next_item_id        = d.get("next_item_id", 11)
                self.next_customer_id    = d.get("next_customer_id", 1)
                self.next_transaction_id = d.get("next_transaction_id", 1)
                self.next_payment_id     = d.get("next_payment_id", 1)
                return
            except Exception:
                messagebox.showerror("Data Error", "JSON corrupted. Starting fresh.")
        self._initialize_default_data()

    def _initialize_default_data(self):
        self.inventory           = [dict(i) for i in SAMPLE_INVENTORY]
        self.transactions        = []
        self.customers           = []
        self.price_history       = {}
        self.khata_payments      = []
        self.next_item_id        = 11
        self.next_customer_id    = 1
        self.next_transaction_id = 1
        self.next_payment_id     = 1

    def _save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "inventory":           self.inventory,
                "transactions":        self.transactions,
                "customers":           self.customers,
                "price_history":       self.price_history,
                "khata_payments":      self.khata_payments,
                "next_item_id":        self.next_item_id,
                "next_customer_id":    self.next_customer_id,
                "next_transaction_id": self.next_transaction_id,
                "next_payment_id":     self.next_payment_id,
            }, f, indent=2, ensure_ascii=False)
        self._set_status("Data saved.")

    # ── KHATA HELPERS ─────────────────────────
    def _get_customer_balance(self, cid):
        billed   = sum(t["total"] for t in self.transactions if t.get("customer_id") == cid)
        paid_in  = sum(t.get("paid", t["total"]) for t in self.transactions if t.get("customer_id") == cid)
        payments = sum(p["amount"] for p in self.khata_payments if p.get("customer_id") == cid)
        return round(billed - paid_in - payments, 2)

    def _record_khata_payment(self, cid, amount, note=""):
        self.khata_payments.append({
            "id":          self.next_payment_id,
            "customer_id": cid,
            "date":        datetime.now().strftime("%Y-%m-%d %H:%M"),
            "amount":      amount,
            "note":        note,
            "by":          "Owner",
        })
        self.next_payment_id += 1
        self._save_data()
        self._refresh_khata_tab()
        self._refresh_customers_table()
        cust = next((c for c in self.customers if c["id"] == cid), None)
        if cust:
            self._set_status(f"Payment Rs. {amount:.2f} recorded for {cust['name']}")

    # ── UI ────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        self._build_nav()
        self._build_content()
        self._build_statusbar()

    def _build_header(self):
        hdr = tk.Frame(self, bg=C["green_dark"])
        hdr.pack(fill="x")
        left = tk.Frame(hdr, bg=C["green_dark"])
        left.pack(side="left", padx=20, pady=12)
        tk.Label(left, text="  Hardware Shop Management System",
                 bg=C["green_dark"], fg=C["white"], font=FONT_TITLE).pack(anchor="w")
        tk.Label(left, text="پارڈویٹر دکان انتظام نظام  |  Inventory · Billing · Khata",
                 bg=C["green_dark"], fg=C["yellow"], font=FONT_SM).pack(anchor="w")
        rounded_button(tk.Frame(hdr, bg=C["green_dark"]).pack(side="right", padx=20, pady=12) or hdr,
                       "↻  Refresh", self._refresh_table, C["yellow"], fg=C["text"]).pack(side="right", padx=20, pady=12)

    def _build_nav(self):
        nav = tk.Frame(self, bg=C["white"])
        nav.pack(fill="x")
        tk.Frame(nav, bg=C["border"], height=1).pack(fill="x", side="bottom")
        self._tabs        = {}
        self._tab_buttons = {}
        for key, label in [
            ("inventory",    "  Inventory   انوینٹری"),
            ("customers",    "  Customers   صارفین"),
            ("billing",      "  Billing   بلنگ"),
            ("transactions", "  Transactions   لین دین"),
            ("khata",        "📒  Khata   کھاتہ"),
            ("reports",      "  Reports   رپورٹس"),
        ]:
            btn = tk.Button(nav, text=label, font=FONT, relief="flat", bd=0,
                            cursor="hand2", padx=13, pady=10,
                            command=lambda k=key: self._switch_tab(k))
            btn.pack(side="left")
            self._tab_buttons[key] = btn
        self._switch_tab("inventory", init=True)

    def _switch_tab(self, key, init=False):
        for k, btn in self._tab_buttons.items():
            if k == key:
                btn.configure(bg=C["green_dark"], fg=C["white"], font=FONT_BOLD)
            else:
                btn.configure(bg=C["white"], fg=C["muted"], font=FONT)
        if not init:
            for f in self._tabs.values():
                f.pack_forget()
            if key in self._tabs:
                self._tabs[key].pack(fill="both", expand=True)
            if key == "khata":
                self._refresh_khata_tab()

    def _build_content(self):
        c = tk.Frame(self, bg=C["bg"])
        c.pack(fill="both", expand=True, padx=10, pady=8)
        self._tabs["inventory"]    = self._build_inventory_tab(c)
        self._tabs["customers"]    = self._build_customers_tab(c)
        self._tabs["billing"]      = self._build_billing_tab(c)
        self._tabs["transactions"] = self._build_transactions_tab(c)
        self._tabs["khata"]        = self._build_khata_tab(c)
        self._tabs["reports"]      = self._build_reports_tab(c)
        self._tabs["inventory"].pack(fill="both", expand=True)

    # ── INVENTORY TAB ─────────────────────────
    def _build_inventory_tab(self, parent):
        frm  = tk.Frame(parent, bg=C["bg"])
        card = tk.Frame(frm, bg=C["white"], relief="flat", bd=1,
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        sh = tk.Frame(card, bg=C["green_dark"])
        sh.pack(fill="x")
        tk.Label(sh, text="☰  Inventory List   انوینٹری فہرست",
                 bg=C["green_dark"], fg=C["white"], font=FONT_BOLD, padx=14, pady=9).pack(side="left")
        br = tk.Frame(sh, bg=C["green_dark"])
        br.pack(side="right", padx=10, pady=6)
        rounded_button(br, "+ Add Item", self._open_add, C["green_light"], padx=10, pady=4).pack(side="left", padx=4)
        rounded_button(br, "⬇ CSV",      self._export_csv,  "#1b5e20", padx=10, pady=4).pack(side="left", padx=4)
        rounded_button(br, "⬇ JSON",     self._export_json, "#1b5e20", padx=10, pady=4).pack(side="left")

        tb = tk.Frame(card, bg=C["white"], pady=8, padx=14)
        tb.pack(fill="x")
        sf = tk.Frame(tb, bg=C["white"])
        sf.pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh_table())
        se = tk.Entry(sf, textvariable=self.search_var, font=FONT, relief="solid", bd=1, width=28)
        se.pack(side="left", padx=6, ipady=4)
        se.insert(0, "تلاش کریں ... Search items...")
        se.bind("<FocusIn>",  lambda e: se.delete(0, "end") if se.get().startswith("تلاش") else None)
        se.bind("<FocusOut>", lambda e: se.insert(0, "تلاش کریں ... Search items...") if not se.get() else None)

        tk.Label(tb, text="Category:", bg=C["white"], font=FONT_SM).pack(side="left", padx=(16, 4))
        self.cat_var = tk.StringVar(value="All")
        cat_cb = ttk.Combobox(tb, textvariable=self.cat_var, values=CATEGORIES,
                               state="readonly", width=14, font=FONT)
        cat_cb.pack(side="left")
        cat_cb.bind("<<ComboboxSelected>>", lambda _: self._refresh_table())

        rtb = tk.Frame(tb, bg=C["white"])
        rtb.pack(side="right")
        self.total_badge = tk.Label(rtb, text="Total: —", bg=C["green_dark"], fg=C["white"],
                                    font=FONT_BOLD, padx=12, pady=4)
        self.total_badge.pack(side="left", padx=4)
        self.value_badge = tk.Label(rtb, text="Value: —", bg=C["yellow"], fg=C["text"],
                                    font=FONT_BOLD, padx=12, pady=4)
        self.value_badge.pack(side="left")

        tf = tk.Frame(card, bg=C["white"])
        tf.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        cols   = ("ID", "Name  نام", "Code  کوڈ", "Price  قیمت", "Stock  اسٹاک", "Value  قدر", "Category  زمرہ")
        widths = [40, 180, 90, 100, 90, 110, 110]
        self.tree = ttk.Treeview(tf, columns=cols, show="headings", selectmode="browse")
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=w, anchor="center")
        vsb = ttk.Scrollbar(tf, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tf, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)
        self.tree.bind("<Double-1>", lambda _: self._open_edit())
        self._style_table()

        af = tk.Frame(card, bg=C["bg"], pady=8, padx=14)
        af.pack(fill="x")
        rounded_button(af, "✏  Edit",          self._open_edit,         C["orange"]).pack(side="left", padx=4)
        rounded_button(af, "  Delete",         self._delete_item,        C["red"]).pack(side="left", padx=4)
        rounded_button(af, "⬆  Update Stock",   self._update_stock,       C["teal"]).pack(side="left", padx=4)
        rounded_button(af, "  Price History",  self._show_price_history, C["blue"]).pack(side="left", padx=4)
        return frm

    def _style_table(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Treeview", background=C["white"], foreground=C["text"],
                    fieldbackground=C["white"], rowheight=34, font=FONT)
        s.configure("Treeview.Heading", background=C["header_row"], foreground=C["text"],
                    font=FONT_BOLD, relief="flat")
        s.map("Treeview", background=[("selected", C["green_mid"])])
        if self.tree:
            self.tree.tag_configure("alt", background=C["row_alt"])
            self.tree.tag_configure("low", background="#fff3f3")

    # ── CUSTOMERS TAB ─────────────────────────
    def _build_customers_tab(self, parent):
        frm  = tk.Frame(parent, bg=C["bg"])
        card = tk.Frame(frm, bg=C["white"], relief="flat", bd=1,
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        sh = tk.Frame(card, bg=C["green_dark"])
        sh.pack(fill="x")
        tk.Label(sh, text="👥  Customers   صارفین کی فہرست",
                 bg=C["green_dark"], fg=C["white"], font=FONT_BOLD, padx=14, pady=9).pack(side="left")
        rounded_button(sh, "+ Add Customer", self._open_add_customer, C["green_light"],
                       padx=10, pady=4).pack(side="right", padx=10, pady=7)

        tb = tk.Frame(card, bg=C["white"], pady=8, padx=14)
        tb.pack(fill="x")
        self.customer_search_var = tk.StringVar()
        self.customer_search_var.trace_add("write", lambda *_: self._refresh_customers_table())
        se = tk.Entry(tb, textvariable=self.customer_search_var, font=FONT,
                      relief="solid", bd=1, width=28)
        se.pack(side="left", padx=6, ipady=4)
        se.insert(0, "تلاش کریں ... Search customers...")
        se.bind("<FocusIn>",  lambda e: se.delete(0, "end") if se.get().startswith("تلاش") else None)
        se.bind("<FocusOut>", lambda e: se.insert(0, "تلاش کریں ... Search customers...") if not se.get() else None)

        tf = tk.Frame(card, bg=C["white"])
        tf.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        cols   = ("ID", "Name  نام", "Contact  رابطہ", "Address  پتہ", "Credit Limit", "Outstanding  ادھار", "Status")
        widths = [40, 150, 115, 190, 95, 120, 90]
        self.customer_tree = ttk.Treeview(tf, columns=cols, show="headings", selectmode="browse")
        for col, w in zip(cols, widths):
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=w, anchor="center")
        vsb = ttk.Scrollbar(tf, orient="vertical",   command=self.customer_tree.yview)
        hsb = ttk.Scrollbar(tf, orient="horizontal", command=self.customer_tree.xview)
        self.customer_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.customer_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)
        self.customer_tree.tag_configure("has_bal", background=C["khata_red"])
        self.customer_tree.tag_configure("clear",   background=C["khata_green"])
        self.customer_tree.bind("<Double-1>", lambda _: self._open_khata_for_selected())

        af = tk.Frame(card, bg=C["bg"], pady=8, padx=14)
        af.pack(fill="x")
        rounded_button(af, "✏  Edit",           self._open_edit_customer,   C["orange"]).pack(side="left", padx=4)
        rounded_button(af, "  Delete",          self._delete_customer,       C["red"]).pack(side="left", padx=4)
        rounded_button(af, "📒  View Khata",     self._open_khata_for_selected, C["purple"]).pack(side="left", padx=4)
        rounded_button(af, "💵  Quick Payment",  self._quick_payment,        C["teal"]).pack(side="left", padx=4)
        return frm

    # ── BILLING TAB ──────────────────────────
    def _build_billing_tab(self, parent):
        frm  = tk.Frame(parent, bg=C["bg"])
        card = tk.Frame(frm, bg=C["white"], relief="flat", bd=1,
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)
        sh = tk.Frame(card, bg=C["green_dark"])
        sh.pack(fill="x")
        tk.Label(sh, text="  Billing   بلنگ", bg=C["green_dark"], fg=C["white"],
                 font=FONT_BOLD, padx=14, pady=9).pack(side="left")
        rounded_button(sh, "➕  New Bill", self._open_billing, C["yellow"],
                       fg=C["text"], padx=10, pady=4).pack(side="right", padx=10, pady=7)
        tk.Label(card,
                 text="Click '+ New Bill' to create a bill.\n"
                      "Choose Cash  نقد  or Credit / ادھار at billing time.\n"
                      "Credit bills are automatically tracked in the Khata tab.",
                 bg=C["white"], fg=C["muted"], font=("Segoe UI", 12), pady=60).pack(expand=True)
        return frm

    def _open_billing(self):
        BillingModal(self, self.inventory, self.customers,
                     self._add_transaction, self._get_customer_balance)

    def _add_transaction(self, cart, total, customer_id, payment_type, paid):
        txn_id = self.next_transaction_id
        self.next_transaction_id += 1
        dt = datetime.now().strftime("%Y-%m-%d %H:%M")
        for e in cart:
            e["item"]["stock"] -= e["qty"]
        items_str = ", ".join(f"{e['item']['name']} x{e['qty']}" for e in cart)
        self.transactions.append({
            "id": txn_id, "date": dt, "items": items_str,
            "total": total, "paid": paid,
            "payment_type": payment_type, "customer_id": customer_id,
        })
        self._save_data()
        self._refresh_table()
        self._refresh_transactions()
        self._refresh_customers_table()
        self._refresh_khata_tab()
        self._refresh_reports()

    # ── TRANSACTIONS TAB ─────────────────────
    def _build_transactions_tab(self, parent):
        frm  = tk.Frame(parent, bg=C["bg"])
        card = tk.Frame(frm, bg=C["white"], relief="flat", bd=1,
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)
        sh = tk.Frame(card, bg=C["green_dark"])
        sh.pack(fill="x")
        tk.Label(sh, text="  Transactions   لین دین", bg=C["green_dark"], fg=C["white"],
                 font=FONT_BOLD, padx=14, pady=9).pack(side="left")

        tb = tk.Frame(card, bg=C["white"], pady=8, padx=14)
        tb.pack(fill="x")
        tk.Label(tb, text="Filter by Customer:", bg=C["white"], font=FONT_SM).pack(side="left", padx=(0, 4))
        self.txn_customer_filter_var = tk.StringVar(value="All Customers")
        self.txn_customer_filter_cb  = ttk.Combobox(tb, textvariable=self.txn_customer_filter_var,
                                                     values=[], state="readonly", width=30, font=FONT)
        self.txn_customer_filter_cb.pack(side="left")
        self.txn_customer_filter_cb.bind("<<ComboboxSelected>>", lambda _: self._refresh_transactions())

        cols = ("ID", "Date", "Customer", "Pay Type", "Items", "Total", "Paid", "Balance")
        ws   = [40, 120, 130, 70, 270, 100, 100, 100]
        self.txn_tree = ttk.Treeview(card, columns=cols, show="headings", height=20)
        for col, w in zip(cols, ws):
            self.txn_tree.heading(col, text=col)
            self.txn_tree.column(col, width=w, anchor="center")
        self.txn_tree.tag_configure("credit_row", background=C["khata_red"])
        vsb = ttk.Scrollbar(card, orient="vertical", command=self.txn_tree.yview)
        self.txn_tree.configure(yscrollcommand=vsb.set)
        self.txn_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        vsb.pack(side="right", fill="y", pady=10)
        return frm

    def _refresh_transactions(self):
        self.txn_tree.delete(*self.txn_tree.get_children())
        sel  = self.txn_customer_filter_var.get()
        fcid = None
        if sel != "All Customers":
            for c in self.customers:
                if f"{c['name']} ({c['contact']})" == sel:
                    fcid = c["id"]; break
        for t in reversed(self.transactions):
            if fcid is not None and t.get("customer_id") != fcid:
                continue
            cname = "Walk-in"
            if t.get("customer_id"):
                cc = next((c for c in self.customers if c["id"] == t["customer_id"]), None)
                if cc: cname = cc["name"]
            paid    = t.get("paid", t["total"])
            balance = round(t["total"] - paid, 2)
            tag     = "credit_row" if balance > 0 else ""
            items_s = t["items"][:38] + "…" if len(t["items"]) > 38 else t["items"]
            self.txn_tree.insert("", "end", tags=(tag,),
                                 values=(t["id"], t["date"], cname,
                                         t.get("payment_type", "Cash"), items_s,
                                         f"Rs. {t['total']:.2f}",
                                         f"Rs. {paid:.2f}",
                                         f"Rs. {balance:.2f}" if balance > 0 else "✔ Paid"))

    def _refresh_transactions_customer_filter_cb(self):
        if self.txn_customer_filter_cb:
            names = ["All Customers"] + [f"{c['name']} ({c['contact']})" for c in self.customers]
            self.txn_customer_filter_cb["values"] = names
            if self.txn_customer_filter_var.get() not in names:
                self.txn_customer_filter_var.set("All Customers")

    # ── KHATA TAB ────────────────────────────
    def _build_khata_tab(self, parent):
        frm  = tk.Frame(parent, bg=C["bg"])
        card = tk.Frame(frm, bg=C["white"], relief="flat", bd=1,
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        sh = tk.Frame(card, bg=C["purple"])
        sh.pack(fill="x")
        tk.Label(sh, text="📒  Khata Book   کھاتہ  —  Outstanding Credit Ledger",
                 bg=C["purple"], fg=C["white"], font=FONT_BOLD, padx=14, pady=9).pack(side="left")
        rounded_button(sh, "↻  Refresh", self._refresh_khata_tab,
                       C["yellow"], fg=C["text"], padx=10, pady=4).pack(side="right", padx=10, pady=7)

        self.khata_summary_frm = tk.Frame(card, bg=C["bg"])
        self.khata_summary_frm.pack(fill="x", padx=14, pady=(10, 0))

        ff = tk.Frame(card, bg=C["white"], pady=6, padx=14)
        ff.pack(fill="x")
        self.khata_filter_var = tk.StringVar(value="Outstanding Only")
        for opt in ["Outstanding Only", "All Customers"]:
            tk.Radiobutton(ff, text=opt, variable=self.khata_filter_var, value=opt,
                           bg=C["white"], font=FONT, activebackground=C["white"],
                           command=self._refresh_khata_tab).pack(side="left", padx=10)

        tf = tk.Frame(card, bg=C["white"])
        tf.pack(fill="both", expand=True, padx=10, pady=(4, 4))
        cols   = ("Customer", "Contact", "Total Billed", "Total Paid", "Outstanding  ادھار", "Credit Limit", "Status")
        widths = [155, 115, 110, 110, 130, 110, 95]
        self.khata_tree = ttk.Treeview(tf, columns=cols, show="headings", selectmode="browse")
        for col, w in zip(cols, widths):
            self.khata_tree.heading(col, text=col)
            self.khata_tree.column(col, width=w, anchor="center")
        vsb = ttk.Scrollbar(tf, orient="vertical", command=self.khata_tree.yview)
        self.khata_tree.configure(yscrollcommand=vsb.set)
        self.khata_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)
        self.khata_tree.tag_configure("outstanding", background=C["khata_red"])
        self.khata_tree.tag_configure("clear",       background=C["khata_green"])
        self.khata_tree.tag_configure("over_limit",  background="#fce4ec")
        self.khata_tree.bind("<Double-1>", lambda _: self._open_khata_from_khata_tab())

        af = tk.Frame(card, bg=C["bg"], pady=8, padx=14)
        af.pack(fill="x")
        rounded_button(af, "📒  Full Ledger",    self._open_khata_from_khata_tab, C["purple"]).pack(side="left", padx=4)
        rounded_button(af, "💵  Record Payment", self._quick_payment_khata,       C["teal"]).pack(side="left", padx=4)
        rounded_button(af, "⬇  Export CSV",      self._export_khata_csv,          C["green_dark"]).pack(side="left", padx=4)
        return frm

    def _refresh_khata_tab(self):
        if not self.khata_tree:
            return
        # Summary
        for w in self.khata_summary_frm.winfo_children():
            w.destroy()
        total_out  = sum(max(0, self._get_customer_balance(c["id"])) for c in self.customers)
        debtors    = sum(1 for c in self.customers if self._get_customer_balance(c["id"]) > 0)
        over_lim   = sum(1 for c in self.customers
                         if c.get("credit_limit", 0) > 0
                         and self._get_customer_balance(c["id"]) > c["credit_limit"])
        for lbl, val, col in [
            ("Total Outstanding  کل ادھار", f"Rs. {total_out:,.2f}", C["red"]),
            ("Customers with Debt",          str(debtors),            C["orange"]),
            ("Over Credit Limit",            str(over_lim),           C["purple"]),
        ]:
            kf = tk.Frame(self.khata_summary_frm, bg=col, padx=20, pady=10)
            kf.pack(side="left", expand=True, fill="x", padx=4, pady=(0, 10))
            tk.Label(kf, text=lbl, bg=col, fg=C["white"], font=FONT_SM).pack()
            tk.Label(kf, text=val, bg=col, fg=C["white"], font=("Segoe UI", 13, "bold")).pack()

        # Table
        self.khata_tree.delete(*self.khata_tree.get_children())
        show_all = self.khata_filter_var.get() == "All Customers"
        for c in self.customers:
            bal    = self._get_customer_balance(c["id"])
            lim    = c.get("credit_limit", 0)
            billed = sum(t["total"] for t in self.transactions if t.get("customer_id") == c["id"])
            paid   = (sum(t.get("paid", t["total"]) for t in self.transactions if t.get("customer_id") == c["id"])
                      + sum(p["amount"] for p in self.khata_payments if p.get("customer_id") == c["id"]))
            if not show_all and bal <= 0:
                continue
            if lim > 0 and bal > lim:
                tag, status = "over_limit", "⚠ Over Limit"
            elif bal > 0:
                tag, status = "outstanding", "📒 Has Debt"
            else:
                tag, status = "clear", "✔ Clear"
            self.khata_tree.insert("", "end", iid=str(c["id"]), tags=(tag,),
                                   values=(c["name"], c["contact"],
                                           f"Rs. {billed:,.2f}", f"Rs. {paid:,.2f}",
                                           f"Rs. {bal:,.2f}" if bal > 0 else "Rs. 0.00",
                                           f"Rs. {lim:,.2f}" if lim > 0 else "No Limit",
                                           status))

    def _sel_khata_cust(self):
        sel = self.khata_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a customer first.")
            return None
        return next((c for c in self.customers if c["id"] == int(sel[0])), None)

    def _open_khata_from_khata_tab(self):
        c = self._sel_khata_cust()
        if c:
            KhataModal(self, c, self.transactions, self.khata_payments, self._record_khata_payment)

    def _quick_payment_khata(self):
        c = self._sel_khata_cust()
        if c: self._do_quick_payment(c)

    def _open_khata_for_selected(self):
        c = self._selected_customer()
        if c:
            KhataModal(self, c, self.transactions, self.khata_payments, self._record_khata_payment)

    def _quick_payment(self):
        c = self._selected_customer()
        if c: self._do_quick_payment(c)

    def _do_quick_payment(self, cust):
        bal = self._get_customer_balance(cust["id"])
        if bal <= 0:
            messagebox.showinfo("No Balance", f"{cust['name']} has no outstanding balance.")
            return
        amount = simpledialog.askfloat(
            "Record Payment  ادائیگی",
            f"Customer: {cust['name']}\nOutstanding: Rs. {bal:,.2f}\n\nEnter payment amount:",
            parent=self, minvalue=0.01, maxvalue=bal)
        if amount:
            self._record_khata_payment(cust["id"], amount)

    # ── REPORTS ──────────────────────────────
    def _build_reports_tab(self, parent):
        frm  = tk.Frame(parent, bg=C["bg"])
        card = tk.Frame(frm, bg=C["white"], relief="flat", bd=1,
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)
        sh = tk.Frame(card, bg=C["green_dark"])
        sh.pack(fill="x")
        tk.Label(sh, text="  Reports   رپورٹس", bg=C["green_dark"], fg=C["white"],
                 font=FONT_BOLD, padx=14, pady=9).pack(side="left")
        rounded_button(sh, "↻ Refresh", self._refresh_reports,
                       C["yellow"], fg=C["text"], padx=10, pady=4).pack(side="right", padx=10, pady=7)

        body = tk.Frame(card, bg=C["white"], padx=20, pady=14)
        body.pack(fill="both", expand=True)
        body.columnconfigure((0, 1), weight=1)
        self.kpi_frm = tk.Frame(body, bg=C["white"])
        self.kpi_frm.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        tk.Label(body, text="⚠  Low Stock (< 20 units)", bg=C["white"],
                 fg=C["red"], font=FONT_BOLD).grid(row=1, column=0, sticky="w")
        self.low_tree = ttk.Treeview(body, columns=("Name", "Code", "Stock"),
                                     show="headings", height=7)
        for col in ("Name", "Code", "Stock"):
            self.low_tree.heading(col, text=col)
            self.low_tree.column(col, width=120, anchor="center")
        self.low_tree.grid(row=2, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(body, text="  Top 5 High-Value Items", bg=C["white"],
                 fg=C["green_dark"], font=FONT_BOLD).grid(row=1, column=1, sticky="w")
        self.top_tree = ttk.Treeview(body, columns=("Name", "Price", "Stock", "Value"),
                                     show="headings", height=7)
        for col in ("Name", "Price", "Stock", "Value"):
            self.top_tree.heading(col, text=col)
            self.top_tree.column(col, width=120, anchor="center")
        self.top_tree.grid(row=2, column=1, sticky="nsew")
        body.rowconfigure(2, weight=1)
        return frm

    def _refresh_reports(self):
        if not hasattr(self, "kpi_frm"):
            return
        for w in self.kpi_frm.winfo_children():
            w.destroy()
        total_items = len(self.inventory)
        total_val   = sum(i["price"] * i["stock"] for i in self.inventory)
        total_sales = sum(t["total"] for t in self.transactions)
        total_out   = sum(max(0, self._get_customer_balance(c["id"])) for c in self.customers)
        low_stock   = sum(1 for i in self.inventory if i["stock"] < 20)
        for lbl, val, col in [
            (" Items",              str(total_items),             C["green_dark"]),
            (" Inventory Value",    f"Rs. {total_val:,.2f}",      C["blue"]),
            (" Total Sales",        f"Rs. {total_sales:,.2f}",    C["orange"]),
            ("📒 Outstanding Khata", f"Rs. {total_out:,.2f}",      C["purple"]),
            ("⚠ Low Stock",          str(low_stock),               C["red"]),
        ]:
            kf = tk.Frame(self.kpi_frm, bg=col, padx=14, pady=12)
            kf.pack(side="left", expand=True, fill="x", padx=3)
            tk.Label(kf, text=lbl, bg=col, fg=C["white"], font=FONT_SM).pack()
            tk.Label(kf, text=val, bg=col, fg=C["white"],
                     font=("Segoe UI", 12, "bold")).pack()

        self.low_tree.delete(*self.low_tree.get_children())
        for i in sorted(self.inventory, key=lambda x: x["stock"]):
            if i["stock"] < 20:
                self.low_tree.insert("", "end", values=(i["name"], i["code"], i["stock"]),
                                     tags=("low",))
        self.low_tree.tag_configure("low", background="#fff3f3")

        self.top_tree.delete(*self.top_tree.get_children())
        for i in sorted(self.inventory, key=lambda x: x["price"] * x["stock"], reverse=True)[:5]:
            v = i["price"] * i["stock"]
            self.top_tree.insert("", "end",
                                 values=(i["name"], f"Rs. {i['price']:.2f}", i["stock"], f"Rs. {v:.2f}"))

    # ── STATUS BAR ───────────────────────────
    def _build_statusbar(self):
        sb = tk.Frame(self, bg=C["green_dark"])
        sb.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(sb, textvariable=self.status_var, bg=C["green_dark"], fg=C["yellow"],
                 font=FONT_SM, padx=14, pady=5).pack(side="left")
        tk.Label(sb, text="Hardware Shop  |  Made in Pakistan 2025 ©  |  پاکستان میں بنایا گیا",
                 bg=C["green_dark"], fg=C["yellow"], font=FONT_SM, padx=14, pady=5).pack(side="right")

    def _set_status(self, msg):
        self.status_var.set(f"✔  {msg}  —  {datetime.now().strftime('%H:%M:%S')}")

    # ── TABLE ────────────────────────────────
    def _get_displayed(self):
        q   = self.search_var.get().lower().strip()
        cat = self.cat_var.get()
        if q.startswith("تلاش"): q = ""
        return [i for i in self.inventory
                if (cat == "All" or i.get("category") == cat)
                and (not q or q in i["name"].lower() or q in i["code"].lower())]

    def _refresh_table(self):
        if not self.tree: return
        self.tree.delete(*self.tree.get_children())
        data = self._get_displayed()
        if self._sort_col:
            km = {"ID": "id", "Name  نام": "name", "Code  کوڈ": "code",
                  "Price  قیمت": "price", "Stock  اسٹاک": "stock",
                  "Value  قدر": "_val", "Category  زمرہ": "category"}
            k = km.get(self._sort_col, "name")
            data = sorted(data, key=lambda x: x["price"]*x["stock"] if k == "_val" else x.get(k, ""),
                          reverse=self._sort_rev)
        total_val = 0.0
        for i, item in enumerate(data):
            v = item["price"] * item["stock"]
            total_val += v
            tag = "low" if item["stock"] < 20 else ("alt" if i % 2 else "")
            self.tree.insert("", "end", iid=str(item["id"]),
                             values=(item["id"], item["name"], item["code"],
                                     f"Rs. {item['price']:.2f}", item["stock"],
                                     f"Rs. {v:.2f}", item.get("category", "—")),
                             tags=(tag,))
        self.total_badge.configure(text=f"Total: {len(data)}")
        self.value_badge.configure(text=f"Value: Rs. {total_val:,.2f}")
        self._set_status(f"Showing {len(data)} of {len(self.inventory)} items")

    def _sort_by(self, col):
        self._sort_rev = not self._sort_rev if self._sort_col == col else False
        self._sort_col = col
        self._refresh_table()

    def _selected_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select an item first.")
            return None
        return next((i for i in self.inventory if i["id"] == int(sel[0])), None)

    # ── ITEM CRUD ─────────────────────────────
    def _open_add(self):
        def cb(data):
            data["id"] = self.next_item_id
            self.next_item_id += 1
            self.inventory.append(data)
            self._refresh_table()
            self._set_status(f"Added: {data['name']}")
        ItemModal(self, cb)

    def _open_edit(self):
        item = self._selected_item()
        if not item: return
        def cb(data):
            data["id"] = item["id"]
            idx = next(i for i, x in enumerate(self.inventory) if x["id"] == item["id"])
            if self.inventory[idx]["price"] != data["price"]:
                PRICE_HISTORY.setdefault(item["id"], []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "old": self.inventory[idx]["price"], "new": data["price"]})
            self.inventory[idx] = data
            self._refresh_table()
            self._set_status(f"Updated: {data['name']}")
        ItemModal(self, cb, item=dict(item))

    def _delete_item(self):
        item = self._selected_item()
        if not item: return
        if messagebox.askyesno("Confirm", f"Delete '{item['name']}'?"):
            self.inventory = [i for i in self.inventory if i["id"] != item["id"]]
            self._refresh_table()
            self._set_status(f"Deleted: {item['name']}")

    def _update_stock(self):
        item = self._selected_item()
        if not item: return
        qty = simpledialog.askinteger("Update Stock",
                                      f"Add quantity to '{item['name']}' (negative to subtract):",
                                      parent=self, minvalue=-item["stock"])
        if qty is None: return
        item["stock"] = max(0, item["stock"] + qty)
        self._refresh_table()
        self._set_status(f"Stock updated: {item['name']} → {item['stock']}")

    def _show_price_history(self):
        item = self._selected_item()
        if not item: return
        hist = PRICE_HISTORY.get(item["id"], [])
        if not hist:
            messagebox.showinfo("Price History", f"No price changes for '{item['name']}'.")
            return
        win = tk.Toplevel(self)
        win.title(f"Price History — {item['name']}")
        win.configure(bg=C["white"])
        win.geometry("420x300")
        tk.Label(win, text=f"Price History: {item['name']}",
                 bg=C["green_dark"], fg=C["white"], font=FONT_BOLD,
                 padx=14, pady=9).pack(fill="x")
        t = ttk.Treeview(win, columns=("Date", "Old Price", "New Price"), show="headings", height=10)
        for col in ("Date", "Old Price", "New Price"):
            t.heading(col, text=col)
            t.column(col, width=130, anchor="center")
        t.pack(fill="both", expand=True, padx=10, pady=10)
        for h in hist:
            t.insert("", "end", values=(h["date"], f"Rs. {h['old']:.2f}", f"Rs. {h['new']:.2f}"))

    # ── CUSTOMER CRUD ─────────────────────────
    def _open_add_customer(self):
        def cb(data):
            data["id"] = self.next_customer_id
            self.next_customer_id += 1
            self.customers.append(data)
            self._refresh_customers_table()
            self._refresh_transactions_customer_filter_cb()
            self._set_status(f"Added: {data['name']}")
        CustomerModal(self, cb)

    def _open_edit_customer(self):
        cust = self._selected_customer()
        if not cust: return
        def cb(data):
            data["id"] = cust["id"]
            idx = next(i for i, x in enumerate(self.customers) if x["id"] == cust["id"])
            self.customers[idx] = data
            self._refresh_customers_table()
            self._refresh_transactions_customer_filter_cb()
            self._set_status(f"Updated: {data['name']}")
        CustomerModal(self, cb, customer=dict(cust))

    def _delete_customer(self):
        cust = self._selected_customer()
        if not cust: return
        if self._get_customer_balance(cust["id"]) > 0:
            messagebox.showerror("Cannot Delete",
                                 f"{cust['name']} has outstanding khata.\nClear it first.")
            return
        if messagebox.askyesno("Confirm", f"Delete '{cust['name']}'?"):
            self.customers = [c for c in self.customers if c["id"] != cust["id"]]
            self._refresh_customers_table()
            self._refresh_transactions_customer_filter_cb()
            self._set_status(f"Deleted: {cust['name']}")

    def _selected_customer(self):
        sel = self.customer_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a customer first.")
            return None
        return next((c for c in self.customers if c["id"] == int(sel[0])), None)

    def _refresh_customers_table(self):
        if not self.customer_tree: return
        self.customer_tree.delete(*self.customer_tree.get_children())
        q = self.customer_search_var.get().lower().strip()
        if q.startswith("تلاش"): q = ""
        for cust in self.customers:
            if q and q not in cust["name"].lower() and q not in cust["contact"].lower():
                continue
            bal = self._get_customer_balance(cust["id"])
            lim = cust.get("credit_limit", 0)
            tag    = "has_bal" if bal > 0 else "clear"
            status = f"📒 Rs. {bal:,.0f}" if bal > 0 else "✔ Clear"
            self.customer_tree.insert("", "end", iid=str(cust["id"]), tags=(tag,),
                                      values=(cust["id"], cust["name"], cust["contact"],
                                              cust["address"],
                                              f"Rs. {lim:,.0f}" if lim > 0 else "No Limit",
                                              f"Rs. {bal:,.2f}" if bal > 0 else "Rs. 0.00",
                                              status))
        self._set_status(f"Showing customers")

    def _apply_customer_filters(self):
        self._refresh_customers_table()

    def _sort_customers_by(self, col):
        self._sort_rev = not self._sort_rev if self._sort_col == col else False
        self._sort_col = col
        self._refresh_customers_table()

    # ── EXPORT ────────────────────────────────
    def _export_csv(self):
        path = "inventory_export.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name", "code", "price", "stock", "category"])
            writer.writeheader()
            writer.writerows(self.inventory)
        messagebox.showinfo("Export", f"Saved to:\n{os.path.abspath(path)}")

    def _export_json(self):
        path = "inventory_export.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.inventory, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Export", f"Saved to:\n{os.path.abspath(path)}")

    def _export_khata_csv(self):
        path = "khata_export.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Customer", "Contact", "Total Billed", "Total Paid", "Outstanding", "Credit Limit"])
            for c in self.customers:
                bal    = self._get_customer_balance(c["id"])
                billed = sum(t["total"] for t in self.transactions if t.get("customer_id") == c["id"])
                paid   = billed - bal
                lim    = c.get("credit_limit", 0)
                w.writerow([c["name"], c["contact"],
                             f"{billed:.2f}", f"{paid:.2f}", f"{bal:.2f}",
                             f"{lim:.2f}" if lim > 0 else "No Limit"])
        messagebox.showinfo("Export", f"Khata saved to:\n{os.path.abspath(path)}")
        self._set_status("Khata CSV exported")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = HardwareShopApp()
    app.mainloop()
