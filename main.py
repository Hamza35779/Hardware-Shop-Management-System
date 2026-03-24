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
}

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SM = ("Segoe UI", 9)

# ─────────────────────────────────────────────
#  DATA FILE
# ─────────────────────────────────────────────
DATA_FILE = "shop_data.json"

# ─────────────────────────────────────────────
#  SAMPLE DATA
# ─────────────────────────────────────────────
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

CATEGORIES = ["All", "Tools", "Fasteners", "Measuring", "Power Tools", "Painting", "Safety"]

SAMPLE_TRANSACTIONS = []
PRICE_HISTORY = {}


# ─────────────────────────────────────────────
#  HELPER WIDGETS
# ─────────────────────────────────────────────
def rounded_button(parent, text, command, bg, fg="#ffffff", padx=14, pady=6, font=FONT_BOLD):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, font=font,
        relief="flat", cursor="hand2",
        padx=padx, pady=pady,
        activebackground=bg, activeforeground=fg,
        bd=0
    )
    return btn


def section_label(parent, text, bg=None):
    bg = bg or C["green_dark"]
    frm = tk.Frame(parent, bg=bg)
    frm.pack(fill="x")
    tk.Label(frm, text=text, bg=bg, fg=C["white"],
             font=FONT_BOLD, padx=14, pady=8).pack(side="left")
    return frm


# ─────────────────────────────────────────────
#  MODAL BASE
# ─────────────────────────────────────────────
class BaseModal(tk.Toplevel):
    def __init__(self, parent, title, width=460, height=420):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=C["white"])
        self.resizable(False, False)
        self.grab_set()
        # Center
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def header(self, text):
        frm = tk.Frame(self, bg=C["green_dark"])
        frm.pack(fill="x")
        tk.Label(frm, text=text, bg=C["green_dark"], fg=C["white"],
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
        ent = tk.Entry(parent, textvariable=var, font=FONT,
                       relief="solid", bd=1,
                       bg=C["white"], fg=C["text"])
        ent.grid(row=row + 1, column=0, sticky="ew", ipady=5)
        return var, ent

    def dropdown(self, parent, label, row, options, default=""):
        tk.Label(parent, text=label, bg=C["white"], fg=C["muted"],
                 font=FONT_SM, anchor="w").grid(row=row, column=0, sticky="w", pady=(8, 1))
        var = tk.StringVar(value=default)
        cb = ttk.Combobox(parent, textvariable=var, values=options,
                          state="readonly", font=FONT)
        cb.grid(row=row + 1, column=0, sticky="ew", ipady=4)
        return var


# ─────────────────────────────────────────────
#  ADD / EDIT ITEM MODAL
# ─────────────────────────────────────────────
class ItemModal(BaseModal):
    def __init__(self, parent, callback, item=None):
        title = "Edit Item" if item else "Add New Item"
        super().__init__(parent, title, 440, 500)
        self.callback = callback
        self.item = item

        self.header(f"{'✏  Edit' if item else '➕  Add'} Item")
        body = self.body_frame()
        body.columnconfigure(0, weight=1)

        v = item or {}
        self.v_name,  _ = self.field(body, "Item Name  (نام)",   0,  v.get("name", ""))
        self.v_code,  _ = self.field(body, "Item Code  (کوڈ)",   2,  v.get("code", ""))
        self.v_price, _ = self.field(body, "Price (Rs.)  (قیمت)", 4, v.get("price", ""))
        self.v_stock, _ = self.field(body, "Stock  (اسٹاک)",     6,  v.get("stock", ""))
        self.v_cat = self.dropdown(body, "Category  (زمرہ)", 8,
                                   [c for c in CATEGORIES if c != "All"],
                                   v.get("category", "Tools"))

        ft = self.footer()
        rounded_button(ft, "Cancel", self.destroy, C["muted"]).pack(side="right", padx=(6, 0))
        rounded_button(ft, "Save  ✔", self._save, C["green_dark"]).pack(side="right")

    def _save(self):
        name  = self.v_name.get().strip()
        code  = self.v_code.get().strip()
        cat   = self.v_cat.get()
        try:
            price = float(self.v_price.get())
            stock = int(self.v_stock.get())
            assert price >= 0 and stock >= 0
        except Exception:
            messagebox.showerror("Validation Error", "Price must be a positive number.\nStock must be a positive integer.")
            return
        if not name or not code:
            messagebox.showerror("Validation Error", "Name and Code are required.")
            return
        self.callback({"name": name, "code": code, "price": price,
                        "stock": stock, "category": cat})
        self.destroy()


# ─────────────────────────────────────────────
#  ADD / EDIT CUSTOMER MODAL
# ─────────────────────────────────────────────
class CustomerModal(BaseModal):
    def __init__(self, parent, callback, customer=None):
        title = "Edit Customer" if customer else "Add New Customer"
        super().__init__(parent, title, 440, 400)
        self.callback = callback
        self.customer = customer

        self.header(f"{'✏  Edit' if customer else '➕  Add'} Customer")
        body = self.body_frame()
        body.columnconfigure(0, weight=1)

        v = customer or {}
        self.v_name,    _ = self.field(body, "Customer Name  (نام)",   0,  v.get("name", ""))
        self.v_contact, _ = self.field(body, "Contact  (رابطہ)",       2,  v.get("contact", ""))
        self.v_address, _ = self.field(body, "Address  (پتہ)",         4,  v.get("address", ""))

        ft = self.footer()
        rounded_button(ft, "Cancel", self.destroy, C["muted"]).pack(side="right", padx=(6, 0))
        rounded_button(ft, "Save  ✔", self._save, C["green_dark"]).pack(side="right")

    def _save(self):
        name    = self.v_name.get().strip()
        contact = self.v_contact.get().strip()
        address = self.v_address.get().strip()

        if not name or not contact:
            messagebox.showerror("Validation Error", "Name and Contact are required.")
            return
        self.callback({"name": name, "contact": contact, "address": address})
        self.destroy()


# ─────────────────────────────────────────────
#  BILLING MODAL
# ─────────────────────────────────────────────
class BillingModal(BaseModal):
    def __init__(self, parent, inventory, customers, add_transaction_cb):
        super().__init__(parent, "Create Bill  بل بنائیں", 600, 560)
        self.inventory = inventory
        self.customers = customers
        self.add_transaction_cb = add_transaction_cb
        self.cart = []

        self.header("  Billing  بلنگ")
        body = tk.Frame(self, bg=C["white"], padx=16, pady=10)
        body.pack(fill="both", expand=True)

        # Customer selector
        cust_frm = tk.Frame(body, bg=C["white"])
        cust_frm.pack(fill="x", pady=(0, 8))
        tk.Label(cust_frm, text="Customer:", bg=C["white"], font=FONT_BOLD).grid(row=0, column=0, sticky="w")
        self.customer_var = tk.StringVar(value="Walk-in Customer")
        customer_names = ["Walk-in Customer"] + [f"{c['name']} ({c['contact']})" for c in customers]
        self.customer_cb = ttk.Combobox(cust_frm, textvariable=self.customer_var, values=customer_names,
                                        state="readonly", width=30, font=FONT)
        self.customer_cb.grid(row=0, column=1, padx=8)
        cust_frm.columnconfigure(1, weight=1)

        # Item selector
        sel_frm = tk.Frame(body, bg=C["white"])
        sel_frm.pack(fill="x", pady=(0, 8))

        tk.Label(sel_frm, text="Item:", bg=C["white"], font=FONT_BOLD).grid(row=0, column=0, sticky="w")
        self.item_var = tk.StringVar()
        names = [f"{i['name']} ({i['code']})" for i in inventory]
        self.item_cb = ttk.Combobox(sel_frm, textvariable=self.item_var, values=names,
                                     state="readonly", width=28, font=FONT)
        self.item_cb.grid(row=0, column=1, padx=8)

        tk.Label(sel_frm, text="Qty:", bg=C["white"], font=FONT_BOLD).grid(row=0, column=2)
        self.qty_var = tk.StringVar(value="1")
        tk.Entry(sel_frm, textvariable=self.qty_var, width=5, font=FONT,
                 relief="solid", bd=1).grid(row=0, column=3, padx=8)
        rounded_button(sel_frm, "Add to Cart", self._add_to_cart, C["green_dark"],
                        padx=10, pady=4).grid(row=0, column=4)

        # Cart table
        cols = ("Item", "Code", "Unit Price", "Qty", "Subtotal")
        self.cart_tree = ttk.Treeview(body, columns=cols, show="headings", height=8)
        widths = [160, 70, 90, 50, 90]
        for col, w in zip(cols, widths):
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=w, anchor="center")
        self.cart_tree.pack(fill="both", expand=True, pady=6)

        # Remove button
        rounded_button(body, "Remove Selected", self._remove_item, C["red"],
                        padx=10, pady=4).pack(anchor="e")

        # Total
        self.total_var = tk.StringVar(value="Total: Rs. 0.00")
        tk.Label(body, textvariable=self.total_var, bg=C["white"],
                 font=("Segoe UI", 13, "bold"), fg=C["green_dark"]).pack(pady=(6, 0))

        ft = self.footer()
        rounded_button(ft, "Cancel", self.destroy, C["muted"]).pack(side="right", padx=(6, 0))
        rounded_button(ft, "Print & Save Bill  ", self._finalize, C["green_dark"]).pack(side="right")

    def _add_to_cart(self):
        sel = self.item_var.get()
        if not sel:
            messagebox.showwarning("Select Item", "Please select an item first.")
            return
        try:
            qty = int(self.qty_var.get())
            assert qty > 0
        except Exception:
            messagebox.showerror("Error", "Enter a valid quantity.")
            return
        idx = self.item_cb["values"].index(sel)
        item = self.inventory[idx]
        if qty > item["stock"]:
            messagebox.showerror("Insufficient Stock",
                                  f"Only {item['stock']} units available.")
            return
        sub = round(item["price"] * qty, 2)
        self.cart.append({"item": item, "qty": qty, "subtotal": sub})
        self.cart_tree.insert("", "end",
                               values=(item["name"], item["code"],
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

    def _finalize(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add items to the cart first.")
            return
        total = sum(e["subtotal"] for e in self.cart)
        
        customer_display_name = self.customer_var.get()
        customer_id = None
        if customer_display_name != "Walk-in Customer":
            # Find the customer ID based on the selected display name
            for c in self.customers:
                if f"{c['name']} ({c['contact']})" == customer_display_name:
                    customer_id = c['id']
                    break

        self.add_transaction_cb(self.cart, total, customer_id)
        messagebox.showinfo("Bill Saved",
                             f"Bill saved successfully!\nTotal: Rs. {total:.2f}")
        self.destroy()


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────
class HardwareShopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hardware Shop Management System  |  پارڈویٹر دکان انتظام نظام")
        self.geometry("1280x760")
        self.minsize(900, 600)
        self.configure(bg=C["bg"])

        # Data persistence
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._load_data()

        # State
        self._search_query = ""
        self._cat_filter = "All"
        self._sort_col = None
        self._sort_rev = False

        # Initialize UI elements to None to prevent AttributeError on early refresh calls
        self.tree = None
        self.customer_tree = None
        self.txn_tree = None
        self.txn_customer_filter_cb = None # For the transactions customer filter combobox

        self._build_ui()
        # Initial refresh calls after UI is built
        self._refresh_table()
        self._refresh_customers_table()
        self._refresh_transactions()
        self._refresh_transactions_customer_filter_cb() # New call
        self._refresh_reports()

    def _on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? All unsaved changes will be lost."):
            self._save_data()
            self.destroy()

    def _load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.inventory = data.get("inventory", [dict(i) for i in SAMPLE_INVENTORY])
                    self.transactions = data.get("transactions", [])
                    self.customers = data.get("customers", [])
                    self.price_history = data.get("price_history", {})
                    self.next_item_id = data.get("next_item_id", max(i["id"] for i in self.inventory) + 1 if self.inventory else 1)
                    self.next_customer_id = data.get("next_customer_id", 1)
                    self.next_transaction_id = data.get("next_transaction_id", 1)
            except json.JSONDecodeError:
                messagebox.showerror("Data Error", "Could not load data. JSON file is corrupted. Starting with fresh data.")
                self._initialize_default_data()
        else:
            self._initialize_default_data()

    def _initialize_default_data(self):
        self.inventory = [dict(i) for i in SAMPLE_INVENTORY]
        self.transactions = []
        self.customers = []
        self.price_history = {}
        self.next_item_id = max(i["id"] for i in self.inventory) + 1 if self.inventory else 1
        self.next_customer_id = 1
        self.next_transaction_id = 1

    def _save_data(self):
        data = {
            "inventory": self.inventory,
            "transactions": self.transactions,
            "customers": self.customers,
            "price_history": self.price_history,
            "next_item_id": self.next_item_id,
            "next_customer_id": self.next_customer_id,
            "next_transaction_id": self.next_transaction_id,
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self._set_status("Data saved successfully.")

    # ── UI STRUCTURE ──────────────────────────
    def _build_ui(self):
        self._build_header()
        self._build_nav()
        self._build_content()
        self._build_statusbar()

    def _build_header(self):
        hdr = tk.Frame(self, bg=C["green_dark"], pady=0)
        hdr.pack(fill="x")

        left = tk.Frame(hdr, bg=C["green_dark"])
        left.pack(side="left", padx=20, pady=12)
        tk.Label(left, text="  Hardware Shop Management System",
                 bg=C["green_dark"], fg=C["white"], font=FONT_TITLE).pack(anchor="w")
        tk.Label(left, text="پارڈویٹر دکان انتظام نظام  |  Inventory & Billing",
                 bg=C["green_dark"], fg=C["yellow"], font=FONT_SM).pack(anchor="w")

        right = tk.Frame(hdr, bg=C["green_dark"])
        right.pack(side="right", padx=20, pady=12)
        rounded_button(right, "↻  Refresh", self._refresh_table, C["yellow"],
                        fg=C["text"]).pack()

    def _build_nav(self):
        nav = tk.Frame(self, bg=C["white"], relief="flat", bd=0)
        nav.pack(fill="x")
        sep = tk.Frame(nav, bg=C["border"], height=1)
        sep.pack(fill="x", side="bottom")

        self._tabs = {}
        tabs = [
            ("inventory",    "  Inventory   انوینٹری"),
            ("customers",    "  Customers   صارفین"),
            ("billing",      "  Billing   بلنگ"),
            ("transactions", "  Transactions   لین دین"),
            ("reports",      "  Reports   رپورٹس"),
        ]
        self._tab_buttons = {}
        for key, label in tabs:
            btn = tk.Button(nav, text=label, font=FONT,
                            relief="flat", bd=0, cursor="hand2",
                            padx=16, pady=10,
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

    def _build_content(self):
        container = tk.Frame(self, bg=C["bg"])
        container.pack(fill="both", expand=True, padx=10, pady=8)

        self._tabs["inventory"]    = self._build_inventory_tab(container)
        self._tabs["customers"]    = self._build_customers_tab(container)
        self._tabs["billing"]      = self._build_billing_tab(container)
        self._tabs["transactions"] = self._build_transactions_tab(container)
        self._tabs["reports"]      = self._build_reports_tab(container)

        # show first tab
        self._tabs["inventory"].pack(fill="both", expand=True)

    # ── INVENTORY TAB ─────────────────────────
    def _build_inventory_tab(self, parent):
        frm = tk.Frame(parent, bg=C["bg"])

        card = tk.Frame(frm, bg=C["white"], relief="flat", bd=1,
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        # Section header
        sh = tk.Frame(card, bg=C["green_dark"])
        sh.pack(fill="x")
        tk.Label(sh, text="☰  Inventory List   انوینٹری فہرست",
                 bg=C["green_dark"], fg=C["white"], font=FONT_BOLD,
                 padx=14, pady=9).pack(side="left")

        btn_row = tk.Frame(sh, bg=C["green_dark"])
        btn_row.pack(side="right", padx=10, pady=6)
        rounded_button(btn_row, "+ Add Item  شامل کریں", self._open_add, C["green_light"],
                        padx=10, pady=4).pack(side="left", padx=4)
        rounded_button(btn_row, "⬇ Export CSV", self._export_csv, "#1b5e20",
                        padx=10, pady=4).pack(side="left", padx=4)
        rounded_button(btn_row, "⬇ Export JSON", self._export_json, "#1b5e20",
                        padx=10, pady=4).pack(side="left")

        # Toolbar
        toolbar = tk.Frame(card, bg=C["white"], pady=8, padx=14)
        toolbar.pack(fill="x")

        # Search
        search_frm = tk.Frame(toolbar, bg=C["white"])
        search_frm.pack(side="left")
        tk.Label(search_frm, text="", bg=C["white"], font=("Segoe UI", 11)).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_filters())
        se = tk.Entry(search_frm, textvariable=self.search_var,
                      font=FONT, relief="solid", bd=1, width=28)
        se.pack(side="left", padx=6, ipady=4)
        se.insert(0, "تلاش کریں ... Search items...")
        se.bind("<FocusIn>",  lambda e: (se.delete(0, "end") if se.get().startswith("تلاش") else None))
        se.bind("<FocusOut>", lambda e: (se.insert(0, "تلاش کریں ... Search items...") if not se.get() else None))

        # Category filter
        tk.Label(toolbar, text="Category:", bg=C["white"], font=FONT_SM).pack(side="left", padx=(16, 4))
        self.cat_var = tk.StringVar(value="All")
        cat_cb = ttk.Combobox(toolbar, textvariable=self.cat_var,
                               values=CATEGORIES, state="readonly", width=14, font=FONT)
        cat_cb.pack(side="left")
        cat_cb.bind("<<ComboboxSelected>>", lambda _: self._apply_filters())

        # Stats badges
        right_tb = tk.Frame(toolbar, bg=C["white"])
        right_tb.pack(side="right")
        self.total_badge = tk.Label(right_tb, text="Total: 10",
                                     bg=C["green_dark"], fg=C["white"], font=FONT_BOLD,
                                     padx=12, pady=4)
        self.total_badge.pack(side="left", padx=4)
        self.value_badge = tk.Label(right_tb, text="Value: Rs. 0.00",
                                     bg=C["yellow"], fg=C["text"], font=FONT_BOLD,
                                     padx=12, pady=4)
        self.value_badge.pack(side="left")

        # Table
        tbl_frm = tk.Frame(card, bg=C["white"])
        tbl_frm.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        cols = ("ID", "Name  نام", "Code  کوڈ", "Price  قیمت",
                "Stock  اسٹاک", "Value  قدر", "Category  زمرہ")
        self.tree = ttk.Treeview(tbl_frm, columns=cols, show="headings",
                                  selectmode="browse")
        widths = [40, 180, 90, 100, 90, 110, 110]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col,
                              command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=w, anchor="center")

        # Scrollbars
        vsb = ttk.Scrollbar(tbl_frm, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tbl_frm, orient="horizontal",  command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tbl_frm.rowconfigure(0, weight=1)
        tbl_frm.columnconfigure(0, weight=1)

        # Double-click to edit
        self.tree.bind("<Double-1>", lambda _: self._open_edit())

        # Action buttons
        act_frm = tk.Frame(card, bg=C["bg"], pady=8, padx=14)
        act_frm.pack(fill="x")
        rounded_button(act_frm, "✏  Edit Selected",   self._open_edit,   C["orange"]).pack(side="left", padx=4)
        rounded_button(act_frm, "  Delete Selected", self._delete_item, C["red"]).pack(side="left", padx=4)
        rounded_button(act_frm, "⬆  Update Stock",    self._update_stock, C["teal"]).pack(side="left", padx=4)
        rounded_button(act_frm, "  Price History",   self._show_price_history, C["blue"]).pack(side="left", padx=4)

        self._style_table()
        return frm

    def _style_table(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background=C["white"],
                         foreground=C["text"],
                         fieldbackground=C["white"],
                         rowheight=34,
                         font=FONT)
        style.configure("Treeview.Heading",
                         background=C["header_row"],
                         foreground=C["text"],
                         font=FONT_BOLD,
                         relief="flat")
        style.map("Treeview", background=[("selected", C["green_mid"])])
        self.tree.tag_configure("alt", background=C["row_alt"])
        self.tree.tag_configure("low",  background="#fff3f3")

    # ── CUSTOMERS TAB ─────────────────────────
    def _build_customers_tab(self, parent):
        frm = tk.Frame(parent, bg=C["bg"])

        card = tk.Frame(frm, bg=C["white"], relief="flat", bd=1,
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        # Section header
        sh = tk.Frame(card, bg=C["green_dark"])
        sh.pack(fill="x")
        tk.Label(sh, text="👥  Customer List   صارفین کی فہرست",
                 bg=C["green_dark"], fg=C["white"], font=FONT_BOLD,
                 padx=14, pady=9).pack(side="left")

        btn_row = tk.Frame(sh, bg=C["green_dark"])
        btn_row.pack(side="right", padx=10, pady=6)
        rounded_button(btn_row, "+ Add Customer  شامل کریں", self._open_add_customer, C["green_light"],
                        padx=10, pady=4).pack(side="left", padx=4)

        # Toolbar (for search/filter customers)
        toolbar = tk.Frame(card, bg=C["white"], pady=8, padx=14)
        toolbar.pack(fill="x")

        # Search
        search_frm = tk.Frame(toolbar, bg=C["white"])
        search_frm.pack(side="left")
        tk.Label(search_frm, text="", bg=C["white"], font=("Segoe UI", 11)).pack(side="left")
        self.customer_search_var = tk.StringVar()
        self.customer_search_var.trace_add("write", lambda *_: self._apply_customer_filters())
        se = tk.Entry(search_frm, textvariable=self.customer_search_var,
                      font=FONT, relief="solid", bd=1, width=28)
        se.pack(side="left", padx=6, ipady=4)
        se.insert(0, "تلاش کریں ... Search customers...")
        se.bind("<FocusIn>",  lambda e: (se.delete(0, "end") if se.get().startswith("تلاش") else None))
        se.bind("<FocusOut>", lambda e: (se.insert(0, "تلاش کریں ... Search customers...") if not se.get() else None))

        # Table
        tbl_frm = tk.Frame(card, bg=C["white"])
        tbl_frm.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        cols = ("ID", "Name  نام", "Contact  رابطہ", "Address  پتہ")
        self.customer_tree = ttk.Treeview(tbl_frm, columns=cols, show="headings",
                                           selectmode="browse")
        widths = [40, 200, 150, 300]
        for col, w in zip(cols, widths):
            self.customer_tree.heading(col, text=col,
                                       command=lambda c=col: self._sort_customers_by(c))
            self.customer_tree.column(col, width=w, anchor="center")

        # Scrollbars
        vsb = ttk.Scrollbar(tbl_frm, orient="vertical",   command=self.customer_tree.yview)
        hsb = ttk.Scrollbar(tbl_frm, orient="horizontal",  command=self.customer_tree.xview)
        self.customer_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.customer_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tbl_frm.rowconfigure(0, weight=1)
        tbl_frm.columnconfigure(0, weight=1)

        # Double-click to edit
        self.customer_tree.bind("<Double-1>", lambda _: self._open_edit_customer())

        # Action buttons
        act_frm = tk.Frame(card, bg=C["bg"], pady=8, padx=14)
        act_frm.pack(fill="x")
        rounded_button(act_frm, "✏  Edit Selected",   self._open_edit_customer,   C["orange"]).pack(side="left", padx=4)
        rounded_button(act_frm, "  Delete Selected", self._delete_customer, C["red"]).pack(side="left", padx=4)

        self._style_table() # Re-use table styling
        return frm

    # ── BILLING TAB ──────────────────────────
    def _build_billing_tab(self, parent):
        frm = tk.Frame(parent, bg=C["bg"])
        card = tk.Frame(frm, bg=C["white"], relief="flat", bd=1,
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        sh = tk.Frame(card, bg=C["green_dark"])
        sh.pack(fill="x")
        tk.Label(sh, text="  Billing   بلنگ",
                 bg=C["green_dark"], fg=C["white"], font=FONT_BOLD,
                 padx=14, pady=9).pack(side="left")
        rounded_button(sh, "➕  New Bill", self._open_billing, C["yellow"],
                        fg=C["text"], padx=10, pady=4).pack(side="right", padx=10, pady=7)

        tk.Label(card,
                 text="Click '+ New Bill' to create a bill and manage sales transactions.\n"
                      "All bills are saved and visible in the Transactions tab.",
                 bg=C["white"], fg=C["muted"], font=("Segoe UI", 12),
                 pady=60).pack(expand=True)
        return frm

    def _open_billing(self):
        BillingModal(self, self.inventory, self.customers, self._add_transaction)

    def _add_transaction(self, cart, total, customer_id=None):
        txn_id = self.next_transaction_id
        self.next_transaction_id += 1
        dt = datetime.now().strftime("%Y-%m-%d %H:%M")
        for entry in cart:
            entry["item"]["stock"] -= entry["qty"]
        items_str = ", ".join(f"{e['item']['name']} x{e['qty']}" for e in cart)
        self.transactions.append({
            "id": txn_id, "date": dt, "items": items_str, "total": total, "customer_id": customer_id
        })
        self._refresh_table()
        self._refresh_transactions()

    # ── TRANSACTIONS TAB ─────────────────────
    def _build_transactions_tab(self, parent):
        frm = tk.Frame(parent, bg=C["bg"])
        card = tk.Frame(frm, bg=C["white"], relief="flat", bd=1,
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        sh = tk.Frame(card, bg=C["green_dark"])
        sh.pack(fill="x")
        tk.Label(sh, text="  Transactions   لین دین",
                 bg=C["green_dark"], fg=C["white"], font=FONT_BOLD,
                 padx=14, pady=9).pack(side="left")

        # Toolbar for filtering
        toolbar = tk.Frame(card, bg=C["white"], pady=8, padx=14)
        toolbar.pack(fill="x")

        tk.Label(toolbar, text="Filter by Customer:", bg=C["white"], font=FONT_SM).pack(side="left", padx=(0, 4))
        self.txn_customer_filter_var = tk.StringVar(value="All Customers")
        self.txn_customer_filter_cb = ttk.Combobox(toolbar, textvariable=self.txn_customer_filter_var,
                                                    values=[], # Initialize with empty list
                                                    state="readonly", width=30, font=FONT)
        self.txn_customer_filter_cb.pack(side="left")
        self.txn_customer_filter_cb.bind("<<ComboboxSelected>>", lambda _: self._refresh_transactions())


        cols = ("ID", "Date", "Customer", "Items", "Total")
        self.txn_tree = ttk.Treeview(card, columns=cols, show="headings", height=22)
        ws = [50, 130, 150, 350, 110]
        for col, w in zip(cols, ws):
            self.txn_tree.heading(col, text=col)
            self.txn_tree.column(col, width=w, anchor="center")
        vsb = ttk.Scrollbar(card, orient="vertical", command=self.txn_tree.yview)
        self.txn_tree.configure(yscrollcommand=vsb.set)

        self.txn_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        vsb.pack(side="right", fill="y", pady=10)
        return frm

    def _refresh_transactions(self):
        self.txn_tree.delete(*self.txn_tree.get_children())
        
        selected_customer_display = self.txn_customer_filter_var.get()
        filtered_customer_id = None
        if selected_customer_display != "All Customers":
            for c in self.customers:
                if f"{c['name']} ({c['contact']})" == selected_customer_display:
                    filtered_customer_id = c['id']
                    break

        for t in reversed(self.transactions):
            if filtered_customer_id is not None and t.get("customer_id") != filtered_customer_id:
                continue

            customer_name = "Walk-in Customer"
            if t.get("customer_id"):
                customer = next((c for c in self.customers if c["id"] == t["customer_id"]), None)
                if customer:
                    customer_name = customer["name"]

            self.txn_tree.insert("", "end",
                                  values=(t["id"], t["date"], customer_name, t["items"],
                                          f"Rs. {t['total']:.2f}"))

    def _refresh_transactions_customer_filter_cb(self):
        if self.txn_customer_filter_cb:
            customer_names = ["All Customers"] + [f"{c['name']} ({c['contact']})" for c in self.customers]
            self.txn_customer_filter_cb["values"] = customer_names
            if self.txn_customer_filter_var.get() not in customer_names:
                self.txn_customer_filter_var.set("All Customers")

    # ── REPORTS TAB ─────────────────────────
    def _build_reports_tab(self, parent):
        frm = tk.Frame(parent, bg=C["bg"])
        card = tk.Frame(frm, bg=C["white"], relief="flat", bd=1,
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="both", expand=True)

        sh = tk.Frame(card, bg=C["green_dark"])
        sh.pack(fill="x")
        tk.Label(sh, text="  Reports   رپورٹس",
                 bg=C["green_dark"], fg=C["white"], font=FONT_BOLD,
                 padx=14, pady=9).pack(side="left")
        rounded_button(sh, " Refresh Reports", self._refresh_reports,
                        C["yellow"], fg=C["text"], padx=10, pady=4).pack(side="right", padx=10, pady=7)

        body = tk.Frame(card, bg=C["white"], padx=20, pady=14)
        body.pack(fill="both", expand=True)
        body.columnconfigure((0, 1), weight=1)

        # KPI cards
        self.kpi_frm = tk.Frame(body, bg=C["white"])
        self.kpi_frm.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))

        # Low stock table
        tk.Label(body, text="⚠  Low Stock Items  (< 20 units)",
                 bg=C["white"], fg=C["red"], font=FONT_BOLD).grid(row=1, column=0, sticky="w")
        ls_cols = ("Name", "Code", "Stock")
        self.low_tree = ttk.Treeview(body, columns=ls_cols, show="headings", height=7)
        for col in ls_cols:
            self.low_tree.heading(col, text=col)
            self.low_tree.column(col, width=120, anchor="center")
        self.low_tree.grid(row=2, column=0, sticky="nsew", padx=(0, 10))

        # Top value table
        tk.Label(body, text="  Top 5 High-Value Items",
                 bg=C["white"], fg=C["green_dark"], font=FONT_BOLD).grid(row=1, column=1, sticky="w")
        tv_cols = ("Name", "Price", "Stock", "Value")
        self.top_tree = ttk.Treeview(body, columns=tv_cols, show="headings", height=7)
        for col in tv_cols:
            self.top_tree.heading(col, text=col)
            self.top_tree.column(col, width=120, anchor="center")
        self.top_tree.grid(row=2, column=1, sticky="nsew")

        body.rowconfigure(2, weight=1)
        self._refresh_reports()
        return frm

    def _refresh_reports(self):
        # KPIs
        for w in self.kpi_frm.winfo_children():
            w.destroy()

        total_items = len(self.inventory)
        total_value = sum(i["price"] * i["stock"] for i in self.inventory)
        total_sales = sum(t["total"] for t in self.transactions)
        low_stock   = sum(1 for i in self.inventory if i["stock"] < 20)

        kpis = [
            (" Total Items",   str(total_items),            C["green_dark"]),
            (" Inventory Value", f"Rs. {total_value:,.2f}", C["blue"]),
            (" Total Sales",   f"Rs. {total_sales:,.2f}",   C["orange"]),
            ("⚠  Low Stock",    str(low_stock),               C["red"]),
        ]
        for label, val, col in kpis:
            kf = tk.Frame(self.kpi_frm, bg=col, padx=20, pady=14, relief="flat")
            kf.pack(side="left", expand=True, fill="x", padx=6)
            tk.Label(kf, text=label, bg=col, fg=C["white"], font=FONT_SM).pack()
            tk.Label(kf, text=val,   bg=col, fg=C["white"],
                     font=("Segoe UI", 14, "bold")).pack()

        # Low stock
        self.low_tree.delete(*self.low_tree.get_children())
        for i in sorted(self.inventory, key=lambda x: x["stock"]):
            if i["stock"] < 20:
                self.low_tree.insert("", "end",
                                      values=(i["name"], i["code"], i["stock"]),
                                      tags=("low",))
        self.low_tree.tag_configure("low", background="#fff3f3")

        # Top value
        self.top_tree.delete(*self.top_tree.get_children())
        top5 = sorted(self.inventory, key=lambda x: x["price"] * x["stock"], reverse=True)[:5]
        for i in top5:
            val = i["price"] * i["stock"]
            self.top_tree.insert("", "end",
                                  values=(i["name"], f"Rs. {i['price']:.2f}",
                                          i["stock"], f"Rs. {val:.2f}"))

    # ── STATUS BAR ───────────────────────────
    def _build_statusbar(self):
        sb = tk.Frame(self, bg=C["green_dark"])
        sb.pack(fill="x", side="bottom")
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(sb, textvariable=self.status_var,
                 bg=C["green_dark"], fg=C["yellow"], font=FONT_SM,
                 padx=14, pady=5).pack(side="left")
        tk.Label(sb,
                 text="Hardware Shop  |  Made in Pakistan 2024 ©  |  پاکستان میں بنایا گیا",
                 bg=C["green_dark"], fg=C["yellow"], font=FONT_SM,
                 padx=14, pady=5).pack(side="right")

    def _set_status(self, msg):
        self.status_var.set(f"✔  {msg}  —  {datetime.now().strftime('%H:%M:%S')}")

    # ── TABLE OPERATIONS ──────────────────────
    def _get_displayed(self):
        q   = self.search_var.get().lower().strip()
        cat = self.cat_var.get()
        if q.startswith("تلاش"): q = ""
        result = []
        for item in self.inventory:
            if cat != "All" and item.get("category") != cat:
                continue
            if q and q not in item["name"].lower() and q not in item["code"].lower():
                continue
            result.append(item)
        return result

    def _apply_filters(self):
        self._refresh_table()

    def _refresh_table(self):
        if not self.tree: # Ensure treeview is built
            return
        self.tree.delete(*self.tree.get_children())
        data = self._get_displayed()

        if self._sort_col:
            key_map = {
                "ID": "id", "Name  نام": "name", "Code  کوڈ": "code",
                "Price  قیمت": "price", "Stock  اسٹاک": "stock",
                "Value  قدر": "_val", "Category  زمرہ": "category"
            }
            k = key_map.get(self._sort_col, "name")
            data = sorted(data,
                          key=lambda x: x["price"] * x["stock"] if k == "_val" else x.get(k, ""),
                          reverse=self._sort_rev)

        total_val = 0.0
        for i, item in enumerate(data):
            val = item["price"] * item["stock"]
            total_val += val
            tag = "alt" if i % 2 else ""
            if item["stock"] < 20:
                tag = "low"
            self.tree.insert("", "end", iid=str(item["id"]),
                              values=(item["id"], item["name"], item["code"],
                                      f"Rs. {item['price']:.2f}",
                                      item["stock"],
                                      f"Rs. {val:.2f}",
                                      item.get("category", "—")),
                              tags=(tag,))

        self.total_badge.configure(text=f"Total: {len(data)}")
        self.value_badge.configure(text=f"Value: Rs. {total_val:,.2f}")
        self._set_status(f"Showing {len(data)} of {len(self.inventory)} items")

    def _sort_by(self, col):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = False
        self._refresh_table()

    def _selected_item(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select an item first.")
            return None
        iid = int(sel[0])
        return next((i for i in self.inventory if i["id"] == iid), None)

    # ── CRUD ──────────────────────────────────
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
        if not item:
            return
        def cb(data):
            data["id"] = item["id"]
            idx = next(i for i, x in enumerate(self.inventory) if x["id"] == item["id"])
            # Track price history
            if self.inventory[idx]["price"] != data["price"]:
                PRICE_HISTORY.setdefault(item["id"], []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "old": self.inventory[idx]["price"],
                    "new": data["price"]
                })
            self.inventory[idx] = data
            self._refresh_table()
            self._set_status(f"Updated: {data['name']}")
        ItemModal(self, cb, item=dict(item))

    def _delete_item(self):
        item = self._selected_item()
        if not item:
            return
        if messagebox.askyesno("Confirm Delete",
                                f"Delete '{item['name']}'?\nThis cannot be undone."):
            self.inventory = [i for i in self.inventory if i["id"] != item["id"]]
            self._refresh_table()
            self._set_status(f"Deleted: {item['name']}")

    def _update_stock(self):
        item = self._selected_item()
        if not item:
            return
        qty = simpledialog.askinteger(
            "Update Stock",
            f"Enter quantity to ADD to '{item['name']}'\n(Use negative to subtract):",
            parent=self, minvalue=-item["stock"])
        if qty is None:
            return
        item["stock"] = max(0, item["stock"] + qty)
        self._refresh_table()
        self._set_status(f"Stock updated: {item['name']} → {item['stock']} units")

    def _show_price_history(self):
        item = self._selected_item()
        if not item:
            return
        hist = PRICE_HISTORY.get(item["id"], [])
        if not hist:
            messagebox.showinfo("Price History",
                                 f"No price changes recorded for '{item['name']}'.")
            return
        win = tk.Toplevel(self)
        win.title(f"Price History — {item['name']}")
        win.configure(bg=C["white"])
        win.geometry("420x300")
        tk.Label(win, text=f"Price History: {item['name']}",
                 bg=C["green_dark"], fg=C["white"], font=FONT_BOLD,
                 padx=14, pady=9).pack(fill="x")
        cols = ("Date", "Old Price", "New Price")
        t = ttk.Treeview(win, columns=cols, show="headings", height=10)
        for c in cols:
            t.heading(c, text=c)
            t.column(c, width=130, anchor="center")
        t.pack(fill="both", expand=True, padx=10, pady=10)
        for h in hist:
            t.insert("", "end", values=(h["date"],
                                         f"Rs. {h['old']:.2f}",
                                         f"Rs. {h['new']:.2f}"))

    # ── CUSTOMER CRUD ─────────────────────────
    def _open_add_customer(self):
        def cb(data):
            data["id"] = self.next_customer_id
            self.next_customer_id += 1
            self.customers.append(data)
            self._refresh_customers_table()
            self._refresh_transactions_customer_filter_cb() # New call
            self._set_status(f"Added customer: {data['name']}")
        CustomerModal(self, cb)

    def _open_edit_customer(self):
        customer = self._selected_customer()
        if not customer:
            return
        def cb(data):
            data["id"] = customer["id"]
            idx = next(i for i, x in enumerate(self.customers) if x["id"] == customer["id"])
            self.customers[idx] = data
            self._refresh_customers_table()
            self._refresh_transactions_customer_filter_cb() # New call
            self._set_status(f"Updated customer: {data['name']}")
        CustomerModal(self, cb, customer=dict(customer))

    def _delete_customer(self):
        customer = self._selected_customer()
        if not customer:
            return
        if messagebox.askyesno("Confirm Delete",
                                f"Delete customer '{customer['name']}'?\nThis cannot be undone."):
            self.customers = [c for c in self.customers if c["id"] != customer["id"]]
            self._refresh_customers_table()
            self._refresh_transactions_customer_filter_cb() # New call
            self._set_status(f"Deleted customer: {customer['name']}")

    def _selected_customer(self):
        sel = self.customer_tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a customer first.")
            return None
        iid = int(sel[0])
        return next((c for c in self.customers if c["id"] == iid), None)

    def _get_displayed_customers(self):
        q = self.customer_search_var.get().lower().strip()
        if q.startswith("تلاش"): q = ""
        result = []
        for customer in self.customers:
            if q and q not in customer["name"].lower() and q not in customer["contact"].lower():
                continue
            result.append(customer)
        return result

    def _apply_customer_filters(self):
        self._refresh_customers_table()

    def _refresh_customers_table(self):
        if not self.customer_tree: # Ensure treeview is built
            return
        self.customer_tree.delete(*self.customer_tree.get_children())
        data = self._get_displayed_customers()

        if self._sort_col: # Re-using item sort logic for now, can be separated later
            key_map = {
                "ID": "id", "Name  نام": "name", "Contact  رابطہ": "contact",
                "Address  پتہ": "address"
            }
            k = key_map.get(self._sort_col, "name")
            data = sorted(data, key=lambda x: x.get(k, ""), reverse=self._sort_rev)

        for i, customer in enumerate(data):
            tag = "alt" if i % 2 else ""
            self.customer_tree.insert("", "end", iid=str(customer["id"]),
                                      values=(customer["id"], customer["name"],
                                              customer["contact"], customer["address"]),
                                      tags=(tag,))
        self._set_status(f"Showing {len(data)} of {len(self.customers)} customers")

    def _sort_customers_by(self, col):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = False
        self._refresh_customers_table()

    # ── EXPORT ───────────────────────────────
    def _export_csv(self):
        path = "inventory_export.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name", "code", "price", "stock", "category"])
            writer.writeheader()
            writer.writerows(self.inventory)
        messagebox.showinfo("Export Successful", f"Inventory exported to:\n{os.path.abspath(path)}")
        self._set_status("CSV exported successfully")

    def _export_json(self):
        path = "inventory_export.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.inventory, f, indent=2, ensure_ascii=False)
        messagebox.showinfo("Export Successful", f"Inventory exported to:\n{os.path.abspath(path)}")
        self._set_status("JSON exported successfully")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = HardwareShopApp()
    app.mainloop()
