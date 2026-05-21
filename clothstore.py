"""
CLOTH STORE MANAGEMENT SYSTEM
Python Turtle GUI + SQLite RDBMS                   
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, font
import turtle
import time
import os

#  DATABASE LAYER

DB_FILE = "cloth_store.db"

def get_conn():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT    NOT NULL UNIQUE,
            created TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            category_id INTEGER NOT NULL,
            price       REAL    NOT NULL,
            stock       INTEGER NOT NULL DEFAULT 0,
            fabric      TEXT,
            color       TEXT,
            size        TEXT,
            added_on    TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            phone   TEXT,
            email   TEXT,
            address TEXT,
            joined  TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            product_id  INTEGER NOT NULL,
            quantity    INTEGER NOT NULL,
            unit_price  REAL    NOT NULL,
            total       REAL    NOT NULL,
            sale_date   TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (product_id)  REFERENCES products(id)
        )
    """)

    import datetime as _dt
    _today = _dt.date.today().isoformat()

    # Seed categories if empty
    c.execute("SELECT COUNT(*) FROM categories")
    if c.fetchone()[0] == 0:
        seeds = [("Men's Wear", _today), ("Women's Wear", _today),
                 ("Kids Wear",  _today), ("Ethnic Wear",  _today),
                 ("Sportswear", _today), ("Accessories",  _today)]
        c.executemany("INSERT INTO categories(name,created) VALUES(?,?)", seeds)

    conn.commit()
    conn.close()

#  TURTLE SPLASH SCREEN

def draw_splash():
    """Drawing an animated splash screen using Python Turtle."""
    screen = turtle.Screen()
    screen.setup(width=700, height=420)
    screen.bgcolor("#1a1a2e")
    screen.title("Cloth Store Management System — Loading…")
    screen.tracer(0)

    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)
    t.penup()

    def draw_rect(x, y, w, h, fill, pen=None):
        t.goto(x, y)
        t.setheading(0)
        t.pendown()
        t.fillcolor(fill)
        if pen:
            t.pencolor(pen)
            t.pensize(2)
        else:
            t.pencolor(fill)
        t.begin_fill()
        for side in [w, h, w, h]:
            t.forward(side)
            t.left(90)
        t.end_fill()
        t.penup()

    def write_text(x, y, text, size=16, bold=False, color="white", align="center"):
        t.goto(x, y)
        style = ("Arial", size, "bold" if bold else "normal")
        t.pencolor(color)
        t.write(text, align=align, font=style)

    # Background card
    draw_rect(-300, -190, 600, 380, "#16213e", "#e94560")

    # Decorative top bar
    draw_rect(-300, 150, 600, 40, "#e94560")

    # Hanger icon (drawn with turtle lines)
    t.goto(0, 120)
    t.pendown()
    t.pencolor("#f5f5f5")
    t.pensize(3)
    # hook
    t.setheading(180)
    t.circle(-15, 180)
    t.setheading(270)
    t.forward(10)
    # bar
    t.setheading(180)
    t.forward(60)
    t.setheading(315)
    t.forward(70)
    t.penup()
    t.goto(60, 90)
    t.pendown()
    t.setheading(225)
    t.forward(70)
    t.penup()

    write_text(0, 40,  "👔  CLOTH STORE",       size=26, bold=True,  color="#e94560")
    write_text(0, 10,  "MANAGEMENT SYSTEM",      size=18, bold=True,  color="#f5f5f5")
    write_text(0, -20, "Fashion · Quality · Style", size=12, color="#a8a8b3")

    # Progress bar base
    draw_rect(-200, -80, 400, 18, "#0f3460")

    screen.update()

    # Animated progress bar
    steps = 40
    for i in range(steps + 1):
        w = int(400 * i / steps)
        draw_rect(-200, -80, w, 18, "#e94560")
        pct = int(100 * i / steps)
        t.goto(0, -110)
        t.pencolor("#a8a8b3")
        # clear previous text area
        draw_rect(-100, -125, 200, 22, "#16213e")
        t.goto(0, -122)
        t.write(f"Loading… {pct}%", align="center", font=("Arial", 11, "normal"))
        screen.update()
        time.sleep(0.03)

    write_text(0, -150, "Initialising database…", size=10, color="#a8a8b3")
    screen.update()
    time.sleep(0.6)

    write_text(0, -165, "✔  Ready!", size=10, color="#4ecca3")
    screen.update()
    time.sleep(0.8)

    screen.bye()

#  COLOUR / STYLE CONSTANTS

DARK_BG   = "#1a1a2e"
CARD_BG   = "#16213e"
ACCENT    = "#e94560"
ACCENT2   = "#4ecca3"
TEXT_MAIN = "#f5f5f5"
TEXT_SUB  = "#a8a8b3"
ENTRY_BG  = "#0f3460"
BTN_RED   = "#c0392b"
BTN_GREEN = "#27ae60"
BTN_BLUE  = "#2980b9"

FONT_H    = ("Segoe UI", 13, "bold")
FONT_N    = ("Segoe UI", 11)
FONT_S    = ("Segoe UI", 10)


#  HELPER WIDGETS

def styled_btn(parent, text, cmd, color=BTN_BLUE, width=14):
    return tk.Button(
        parent, text=text, command=cmd,
        bg=color, fg="white", activebackground=color,
        font=FONT_S, relief="flat", cursor="hand2",
        width=width, pady=5
    )

def styled_label(parent, text, size=11, bold=False, fg=TEXT_MAIN):
    style = "bold" if bold else "normal"
    return tk.Label(parent, text=text, bg=CARD_BG,
                    fg=fg, font=("Segoe UI", size, style))

def styled_entry(parent, textvariable=None, width=25):
    kw = dict(bg=ENTRY_BG, fg=TEXT_MAIN, insertbackground=TEXT_MAIN,
              font=FONT_N, relief="flat", bd=5, width=width)
    if textvariable:
        kw["textvariable"] = textvariable
    return tk.Entry(parent, **kw)

def section_frame(parent, title):
    outer = tk.LabelFrame(parent, text=f"  {title}  ",
                          bg=CARD_BG, fg=ACCENT, font=FONT_H,
                          relief="groove", bd=2, pady=8, padx=8)
    return outer


#  PAGES

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=DARK_BG)
        self.controller = controller
        self._build()

    def _build(self):
        tk.Label(self, text="📊  Dashboard", bg=DARK_BG,
                 fg=ACCENT, font=("Segoe UI", 18, "bold")).pack(pady=(18, 6))
        tk.Label(self, text="Real-time store overview", bg=DARK_BG,
                 fg=TEXT_SUB, font=FONT_S).pack()

        self.cards_frame = tk.Frame(self, bg=DARK_BG)
        self.cards_frame.pack(pady=20, fill="x", padx=30)

        self.recent_frame = tk.Frame(self, bg=DARK_BG)
        self.recent_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self.refresh()

    def refresh(self):
        for w in self.cards_frame.winfo_children():
            w.destroy()
        for w in self.recent_frame.winfo_children():
            w.destroy()

        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM products")
        total_products = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(stock),0) FROM products")
        total_stock = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM customers")
        total_customers = c.fetchone()[0]
        c.execute("SELECT COALESCE(SUM(total),0) FROM sales")
        total_revenue = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM sales")
        total_sales = c.fetchone()[0]
        c.execute("""
            SELECT p.name, s.quantity, s.total, s.sale_date
            FROM sales s JOIN products p ON s.product_id=p.id
            ORDER BY s.id DESC LIMIT 5
        """)
        recent = c.fetchall()
        conn.close()

        metrics = [
            ("🧾 Products",    total_products,            ACCENT),
            ("📦 Stock Units", total_stock,               "#f39c12"),
            ("👥 Customers",   total_customers,           ACCENT2),
            ("💰 Revenue",     f"₹{total_revenue:,.2f}", BTN_GREEN),
            ("🛒 Sales",       total_sales,               BTN_BLUE),
        ]
        for i, (label, val, col) in enumerate(metrics):
            card = tk.Frame(self.cards_frame, bg=CARD_BG, bd=0, relief="flat",
                            padx=16, pady=14)
            card.grid(row=0, column=i, padx=8, sticky="nsew")
            self.cards_frame.columnconfigure(i, weight=1)
            tk.Label(card, text=label, bg=CARD_BG, fg=TEXT_SUB,
                     font=FONT_S).pack()
            tk.Label(card, text=str(val), bg=CARD_BG, fg=col,
                     font=("Segoe UI", 20, "bold")).pack()

        # Recent sales table
        tk.Label(self.recent_frame, text="Recent Sales",
                 bg=DARK_BG, fg=TEXT_MAIN, font=FONT_H).pack(anchor="w")

        cols = ("Product", "Qty", "Amount", "Date")
        tree = ttk.Treeview(self.recent_frame, columns=cols, show="headings",
                            height=5)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=160)
        for row in recent:
            tree.insert("", "end", values=row)
        tree.pack(fill="x", pady=6)
        self._style_tree(tree)

    def _style_tree(self, tree):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=CARD_BG, foreground=TEXT_MAIN,
                        fieldbackground=CARD_BG, rowheight=28,
                        font=FONT_S)
        style.configure("Treeview.Heading", background=ACCENT,
                        foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)])


# PRODUCTS PAGE 

class ProductsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=DARK_BG)
        self.controller = controller
        self.selected_id = None
        self._build()

    def _build(self):
        tk.Label(self, text="🧵  Products", bg=DARK_BG,
                 fg=ACCENT, font=("Segoe UI", 18, "bold")).pack(pady=(18, 4))

        main = tk.Frame(self, bg=DARK_BG)
        main.pack(fill="both", expand=True, padx=20, pady=8)

        # ── Form ──
        form = section_frame(main, "Add / Edit Product")
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)

        self.v_name  = tk.StringVar()
        self.v_price = tk.StringVar()
        self.v_stock = tk.StringVar()
        self.v_fab   = tk.StringVar()
        self.v_color = tk.StringVar()
        self.v_size  = tk.StringVar()
        self.v_cat   = tk.StringVar()

        fields = [
            ("Name",     self.v_name),
            ("Price ₹", self.v_price),
            ("Stock",    self.v_stock),
            ("Fabric",   self.v_fab),
            ("Color",    self.v_color),
            ("Size",     self.v_size),
        ]
        for i, (lbl, var) in enumerate(fields):
            styled_label(form, lbl).grid(row=i, column=0, sticky="w", pady=3)
            styled_entry(form, textvariable=var).grid(row=i, column=1, pady=3, padx=6)

        styled_label(form, "Category").grid(row=len(fields), column=0, sticky="w", pady=3)
        self.cat_cb = ttk.Combobox(form, textvariable=self.v_cat, width=22,
                                   state="readonly", font=FONT_N)
        self.cat_cb.grid(row=len(fields), column=1, pady=3, padx=6)
        self._load_categories()

        btn_row = tk.Frame(form, bg=CARD_BG)
        btn_row.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)
        styled_btn(btn_row, "➕ Add",    self.add_product,    BTN_GREEN, 10).pack(side="left", padx=4)
        styled_btn(btn_row, "✏ Update", self.update_product,  BTN_BLUE,  10).pack(side="left", padx=4)
        styled_btn(btn_row, "🗑 Delete", self.delete_product,  BTN_RED,   10).pack(side="left", padx=4)
        styled_btn(btn_row, "🔄 Clear",  self.clear_form,     "#7f8c8d", 10).pack(side="left", padx=4)

        # ── Table ──
        tbl_frame = section_frame(main, "Product Inventory")
        tbl_frame.grid(row=0, column=1, sticky="nsew")
        main.rowconfigure(0, weight=1)

        # Search bar
        sf = tk.Frame(tbl_frame, bg=CARD_BG)
        sf.pack(fill="x", pady=(0, 6))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self.load_products())
        styled_label(sf, "🔍 Search:").pack(side="left")
        styled_entry(sf, textvariable=self.search_var, width=20).pack(side="left", padx=6)

        cols = ("ID","Name","Category","Price","Stock","Fabric","Color","Size")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings", height=16)
        widths   = [40, 130, 100, 70, 60, 80, 70, 60]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=w)

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self._apply_treeview_style()
        self.load_products()

    def _apply_treeview_style(self):
        s = ttk.Style()
        s.configure("Treeview", background=CARD_BG, foreground=TEXT_MAIN,
                    fieldbackground=CARD_BG, rowheight=26, font=FONT_S)
        s.configure("Treeview.Heading", background=ACCENT,
                    foreground="white", font=("Segoe UI", 10, "bold"))
        s.map("Treeview", background=[("selected", ACCENT)])

    def _load_categories(self):
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT name FROM categories ORDER BY name")
        cats = [r[0] for r in c.fetchall()]
        conn.close()
        self.cat_cb["values"] = cats
        if cats:
            self.v_cat.set(cats[0])

    def load_products(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        conn = get_conn(); c = conn.cursor()
        q = "%" + self.search_var.get() + "%"
        c.execute("""
            SELECT p.id, p.name, cat.name, p.price, p.stock,
                   p.fabric, p.color, p.size
            FROM products p
            JOIN categories cat ON p.category_id = cat.id
            WHERE p.name LIKE ? OR cat.name LIKE ? OR p.fabric LIKE ?
            ORDER BY p.id DESC
        """, (q, q, q))
        for row in c.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        self.selected_id = vals[0]
        self.v_name.set(vals[1]);  self.v_cat.set(vals[2])
        self.v_price.set(vals[3]); self.v_stock.set(vals[4])
        self.v_fab.set(vals[5]);   self.v_color.set(vals[6])
        self.v_size.set(vals[7])

    def _get_cat_id(self, name):
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT id FROM categories WHERE name=?", (name,))
        row = c.fetchone(); conn.close()
        return row[0] if row else None

    def _validate(self):
        if not self.v_name.get().strip():
            messagebox.showerror("Error", "Product name required"); return False
        try:
            float(self.v_price.get())
            int(self.v_stock.get())
        except ValueError:
            messagebox.showerror("Error", "Price and Stock must be numbers"); return False
        if not self.v_cat.get():
            messagebox.showerror("Error", "Select a category"); return False
        return True

    def add_product(self):
        if not self._validate(): return
        import datetime as _dt
        cat_id = self._get_cat_id(self.v_cat.get())
        conn = get_conn(); c = conn.cursor()
        c.execute("""
            INSERT INTO products(name,category_id,price,stock,fabric,color,size,added_on)
            VALUES(?,?,?,?,?,?,?,?)
        """, (self.v_name.get(), cat_id, float(self.v_price.get()),
              int(self.v_stock.get()), self.v_fab.get(),
              self.v_color.get(), self.v_size.get(),
              _dt.date.today().isoformat()))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", "Product added!")
        self.clear_form(); self.load_products()

    def update_product(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Select a product first"); return
        if not self._validate(): return
        cat_id = self._get_cat_id(self.v_cat.get())
        conn = get_conn(); c = conn.cursor()
        c.execute("""
            UPDATE products SET name=?,category_id=?,price=?,stock=?,
            fabric=?,color=?,size=? WHERE id=?
        """, (self.v_name.get(), cat_id, float(self.v_price.get()),
              int(self.v_stock.get()), self.v_fab.get(),
              self.v_color.get(), self.v_size.get(), self.selected_id))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", "Product updated!")
        self.clear_form(); self.load_products()

    def delete_product(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Select a product first"); return
        if not messagebox.askyesno("Confirm", "Delete this product?"): return
        conn = get_conn(); c = conn.cursor()
        c.execute("DELETE FROM products WHERE id=?", (self.selected_id,))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", "Product deleted!")
        self.clear_form(); self.load_products()

    def clear_form(self):
        self.selected_id = None
        for v in [self.v_name, self.v_price, self.v_stock,
                  self.v_fab, self.v_color, self.v_size]:
            v.set("")
        self._load_categories()


#  CUSTOMERS PAGE 

class CustomersPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=DARK_BG)
        self.controller = controller
        self.selected_id = None
        self._build()

    def _build(self):
        tk.Label(self, text="👥  Customers", bg=DARK_BG,
                 fg=ACCENT, font=("Segoe UI", 18, "bold")).pack(pady=(18, 4))

        main = tk.Frame(self, bg=DARK_BG)
        main.pack(fill="both", expand=True, padx=20, pady=8)

        form = section_frame(main, "Add / Edit Customer")
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)

        self.v_name    = tk.StringVar()
        self.v_phone   = tk.StringVar()
        self.v_email   = tk.StringVar()
        self.v_address = tk.StringVar()

        for i, (lbl, var) in enumerate([
            ("Name",    self.v_name),
            ("Phone",   self.v_phone),
            ("Email",   self.v_email),
            ("Address", self.v_address),
        ]):
            styled_label(form, lbl).grid(row=i, column=0, sticky="w", pady=4)
            styled_entry(form, textvariable=var).grid(row=i, column=1, pady=4, padx=6)

        btn_row = tk.Frame(form, bg=CARD_BG)
        btn_row.grid(row=4, column=0, columnspan=2, pady=12)
        styled_btn(btn_row, "➕ Add",    self.add_customer,    BTN_GREEN, 10).pack(side="left", padx=4)
        styled_btn(btn_row, "✏ Update", self.update_customer,  BTN_BLUE,  10).pack(side="left", padx=4)
        styled_btn(btn_row, "🗑 Delete", self.delete_customer,  BTN_RED,   10).pack(side="left", padx=4)
        styled_btn(btn_row, "🔄 Clear",  self.clear_form,     "#7f8c8d", 10).pack(side="left", padx=4)

        tbl_frame = section_frame(main, "Customer List")
        tbl_frame.grid(row=0, column=1, sticky="nsew")
        main.rowconfigure(0, weight=1)

        sf = tk.Frame(tbl_frame, bg=CARD_BG)
        sf.pack(fill="x", pady=(0, 6))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self.load_customers())
        styled_label(sf, "🔍 Search:").pack(side="left")
        styled_entry(sf, textvariable=self.search_var, width=20).pack(side="left", padx=6)

        cols = ("ID", "Name", "Phone", "Email", "Address", "Joined")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings", height=16)
        ws = [40, 130, 100, 150, 150, 90]
        for col, w in zip(cols, ws):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=w)

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.load_customers()

    def load_customers(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        conn = get_conn(); c = conn.cursor()
        q = "%" + self.search_var.get() + "%"
        c.execute("""SELECT id,name,phone,email,address,joined FROM customers
                     WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
                     ORDER BY id DESC""", (q, q, q))
        for row in c.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], "values")
        self.selected_id = vals[0]
        self.v_name.set(vals[1]); self.v_phone.set(vals[2])
        self.v_email.set(vals[3]); self.v_address.set(vals[4])

    def add_customer(self):
        if not self.v_name.get().strip():
            messagebox.showerror("Error", "Name required"); return
        import datetime as _dt
        conn = get_conn(); c = conn.cursor()
        c.execute("INSERT INTO customers(name,phone,email,address,joined) VALUES(?,?,?,?,?)",
                  (self.v_name.get(), self.v_phone.get(),
                   self.v_email.get(), self.v_address.get(),
                   _dt.date.today().isoformat()))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", "Customer added!")
        self.clear_form(); self.load_customers()

    def update_customer(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Select a customer first"); return
        conn = get_conn(); c = conn.cursor()
        c.execute("UPDATE customers SET name=?,phone=?,email=?,address=? WHERE id=?",
                  (self.v_name.get(), self.v_phone.get(),
                   self.v_email.get(), self.v_address.get(), self.selected_id))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", "Customer updated!")
        self.clear_form(); self.load_customers()

    def delete_customer(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Select a customer first"); return
        if not messagebox.askyesno("Confirm", "Delete this customer?"): return
        conn = get_conn(); c = conn.cursor()
        c.execute("DELETE FROM customers WHERE id=?", (self.selected_id,))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", "Customer deleted!")
        self.clear_form(); self.load_customers()

    def clear_form(self):
        self.selected_id = None
        for v in [self.v_name, self.v_phone, self.v_email, self.v_address]:
            v.set("")


# ───── SALES PAGE ─────────────────────────────

class SalesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=DARK_BG)
        self.controller = controller
        self._build()

    def _build(self):
        tk.Label(self, text="🛒  New Sale", bg=DARK_BG,
                 fg=ACCENT, font=("Segoe UI", 18, "bold")).pack(pady=(18, 4))

        main = tk.Frame(self, bg=DARK_BG)
        main.pack(fill="both", expand=True, padx=20, pady=8)

        form = section_frame(main, "Record Sale")
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=2)

        self.v_prod  = tk.StringVar()
        self.v_cust  = tk.StringVar()
        self.v_qty   = tk.StringVar(value="1")
        self.v_info  = tk.StringVar()

        styled_label(form, "Product").grid(row=0, column=0, sticky="w", pady=4)
        self.prod_cb = ttk.Combobox(form, textvariable=self.v_prod,
                                    width=24, state="readonly", font=FONT_N)
        self.prod_cb.grid(row=0, column=1, pady=4, padx=6)
        self.prod_cb.bind("<<ComboboxSelected>>", self._show_product_info)

        styled_label(form, "Customer\n(optional)").grid(row=1, column=0, sticky="w", pady=4)
        self.cust_cb = ttk.Combobox(form, textvariable=self.v_cust,
                                    width=24, state="readonly", font=FONT_N)
        self.cust_cb.grid(row=1, column=1, pady=4, padx=6)

        styled_label(form, "Quantity").grid(row=2, column=0, sticky="w", pady=4)
        styled_entry(form, textvariable=self.v_qty, width=26).grid(row=2, column=1, pady=4, padx=6)

        styled_label(form, "Product Info", fg=TEXT_SUB).grid(row=3, column=0, sticky="w", pady=4)
        tk.Label(form, textvariable=self.v_info, bg=CARD_BG, fg=ACCENT2,
                 font=FONT_S, wraplength=240).grid(row=3, column=1, pady=4, padx=6, sticky="w")

        styled_btn(form, "✅ Record Sale", self.record_sale, BTN_GREEN, 18
                   ).grid(row=4, column=0, columnspan=2, pady=14)

        # Sales history
        tbl_frame = section_frame(main, "Sales History")
        tbl_frame.grid(row=0, column=1, sticky="nsew")
        main.rowconfigure(0, weight=1)

        cols = ("ID","Product","Customer","Qty","Unit Price","Total","Date")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings", height=16)
        ws = [35, 130, 110, 40, 80, 80, 130]
        for col, w in zip(cols, ws):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=w)

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._load_combos()
        self.load_sales()

    def _load_combos(self):
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT id,name,price,stock FROM products ORDER BY name")
        prods = c.fetchall()
        c.execute("SELECT id,name FROM customers ORDER BY name")
        custs = c.fetchall()
        conn.close()
        self._prod_map = {f"{r[1]} (₹{r[2]}, Stock:{r[3]})": r for r in prods}
        self._cust_map = {r[1]: r[0] for r in custs}
        self.prod_cb["values"] = list(self._prod_map.keys())
        self.cust_cb["values"] = ["— Walk-in —"] + list(self._cust_map.keys())
        self.v_cust.set("— Walk-in —")

    def _show_product_info(self, event):
        key = self.v_prod.get()
        if key in self._prod_map:
            r = self._prod_map[key]
            self.v_info.set(f"ID:{r[0]}  Price:₹{r[2]}  Stock:{r[3]}")

    def record_sale(self):
        if not self.v_prod.get():
            messagebox.showerror("Error", "Select a product"); return
        try:
            qty = int(self.v_qty.get())
            assert qty > 0
        except:
            messagebox.showerror("Error", "Quantity must be a positive integer"); return

        prod = self._prod_map.get(self.v_prod.get())
        if not prod:
            messagebox.showerror("Error", "Invalid product"); return
        prod_id, prod_name, price, stock = prod
        if qty > stock:
            messagebox.showerror("Error", f"Insufficient stock (available: {stock})"); return

        cust_key = self.v_cust.get()
        cust_id  = self._cust_map.get(cust_key) if cust_key != "— Walk-in —" else None
        total    = qty * price
        import datetime as _dt

        conn = get_conn(); c = conn.cursor()
        c.execute("""INSERT INTO sales(customer_id,product_id,quantity,unit_price,total,sale_date)
                     VALUES(?,?,?,?,?,?)""",
                  (cust_id, prod_id, qty, price, total,
                   _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        c.execute("UPDATE products SET stock=stock-? WHERE id=?", (qty, prod_id))
        conn.commit(); conn.close()

        messagebox.showinfo("Sale Recorded",
            f"✅ Sale complete!\nProduct : {prod_name}\n"
            f"Qty     : {qty}\nTotal   : ₹{total:,.2f}")
        self.v_prod.set(""); self.v_qty.set("1"); self.v_info.set("")
        self._load_combos(); self.load_sales()
        self.controller.refresh_dashboard()

    def load_sales(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        conn = get_conn(); c = conn.cursor()
        c.execute("""
            SELECT s.id, p.name,
                   COALESCE(cu.name,'Walk-in'),
                   s.quantity, s.unit_price, s.total, s.sale_date
            FROM sales s
            JOIN products p ON s.product_id=p.id
            LEFT JOIN customers cu ON s.customer_id=cu.id
            ORDER BY s.id DESC
        """)
        for row in c.fetchall():
            vals = list(row)
            vals[5] = f"₹{vals[5]:,.2f}"
            self.tree.insert("", "end", values=vals)
        conn.close()


# CATEGORIES PAGE 

class CategoriesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=DARK_BG)
        self.controller = controller
        self.selected_id = None
        self._build()

    def _build(self):
        tk.Label(self, text="🏷  Categories", bg=DARK_BG,
                 fg=ACCENT, font=("Segoe UI", 18, "bold")).pack(pady=(18, 4))

        main = tk.Frame(self, bg=DARK_BG)
        main.pack(fill="both", expand=True, padx=60, pady=8)
        main.columnconfigure(0, weight=1)

        form = section_frame(main, "Manage Categories")
        form.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.v_name = tk.StringVar()
        styled_label(form, "Category Name").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        styled_entry(form, textvariable=self.v_name, width=30).grid(row=0, column=1, padx=6, pady=6)

        btn_row = tk.Frame(form, bg=CARD_BG)
        btn_row.grid(row=1, column=0, columnspan=2, pady=8)
        styled_btn(btn_row, "➕ Add",    self.add_cat,    BTN_GREEN, 10).pack(side="left", padx=4)
        styled_btn(btn_row, "✏ Update", self.update_cat,  BTN_BLUE,  10).pack(side="left", padx=4)
        styled_btn(btn_row, "🗑 Delete", self.delete_cat,  BTN_RED,   10).pack(side="left", padx=4)

        tbl_frame = section_frame(main, "Category List")
        tbl_frame.grid(row=1, column=0, sticky="nsew")
        main.rowconfigure(1, weight=1)

        cols = ("ID", "Name", "Created")
        self.tree = ttk.Treeview(tbl_frame, columns=cols, show="headings", height=14)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=180)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.load_categories()

    def load_categories(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT id,name,created FROM categories ORDER BY id")
        for row in c.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], "values")
        self.selected_id = vals[0]
        self.v_name.set(vals[1])

    def add_cat(self):
        name = self.v_name.get().strip()
        if not name: messagebox.showerror("Error", "Category name required"); return
        import datetime as _dt
        try:
            conn = get_conn(); c = conn.cursor()
            c.execute("INSERT INTO categories(name,created) VALUES(?,?)",
                      (name, _dt.date.today().isoformat()))
            conn.commit(); conn.close()
            messagebox.showinfo("Success", "Category added!")
            self.v_name.set(""); self.load_categories()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Category already exists")

    def update_cat(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Select a category"); return
        name = self.v_name.get().strip()
        if not name: return
        conn = get_conn(); c = conn.cursor()
        c.execute("UPDATE categories SET name=? WHERE id=?", (name, self.selected_id))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", "Category updated!")
        self.selected_id = None; self.v_name.set(""); self.load_categories()

    def delete_cat(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Select a category"); return
        if not messagebox.askyesno("Confirm", "Delete category?"): return
        conn = get_conn(); c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM products WHERE category_id=?", (self.selected_id,))
        if c.fetchone()[0] > 0:
            messagebox.showerror("Error", "Cannot delete — products exist in this category")
            conn.close(); return
        c.execute("DELETE FROM categories WHERE id=?", (self.selected_id,))
        conn.commit(); conn.close()
        messagebox.showinfo("Success", "Category deleted!")
        self.selected_id = None; self.v_name.set(""); self.load_categories()


#REPORTS PAGE 

class ReportsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=DARK_BG)
        self.controller = controller
        self._build()

    def _build(self):
        tk.Label(self, text="📈  Reports", bg=DARK_BG,
                 fg=ACCENT, font=("Segoe UI", 18, "bold")).pack(pady=(18, 4))

        main = tk.Frame(self, bg=DARK_BG)
        main.pack(fill="both", expand=True, padx=20, pady=8)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

        # Low Stock
        low = section_frame(main, "⚠ Low Stock Alert (stock < 5)")
        low.grid(row=0, column=0, sticky="nsew", padx=(0,10), pady=(0,10))
        cols = ("Product","Category","Stock","Price")
        self.low_tree = ttk.Treeview(low, columns=cols, show="headings", height=8)
        for col in cols:
            self.low_tree.heading(col, text=col)
            self.low_tree.column(col, anchor="center", width=110)
        self.low_tree.pack(fill="both", expand=True)

        # Top Products
        top = section_frame(main, "🏆 Top 10 Best-Selling Products")
        top.grid(row=0, column=1, sticky="nsew", pady=(0,10))
        cols2 = ("Product","Units Sold","Revenue")
        self.top_tree = ttk.Treeview(top, columns=cols2, show="headings", height=8)
        for col in cols2:
            self.top_tree.heading(col, text=col)
            self.top_tree.column(col, anchor="center", width=130)
        self.top_tree.pack(fill="both", expand=True)

        # Category Revenue
        cat_rev = section_frame(main, "💰 Revenue by Category")
        cat_rev.grid(row=1, column=0, sticky="nsew", padx=(0,10))
        cols3 = ("Category","Sales","Revenue")
        self.cat_tree = ttk.Treeview(cat_rev, columns=cols3, show="headings", height=8)
        for col in cols3:
            self.cat_tree.heading(col, text=col)
            self.cat_tree.column(col, anchor="center", width=140)
        self.cat_tree.pack(fill="both", expand=True)

        # Customer Revenue
        cust_rev = section_frame(main, "👑 Top Customers")
        cust_rev.grid(row=1, column=1, sticky="nsew")
        cols4 = ("Customer","Purchases","Total Spent")
        self.cust_tree = ttk.Treeview(cust_rev, columns=cols4, show="headings", height=8)
        for col in cols4:
            self.cust_tree.heading(col, text=col)
            self.cust_tree.column(col, anchor="center", width=140)
        self.cust_tree.pack(fill="both", expand=True)

        styled_btn(self, "🔄 Refresh Reports", self.load_reports,
                   BTN_BLUE, 22).pack(pady=10)
        self.load_reports()

    def load_reports(self):
        conn = get_conn(); c = conn.cursor()

        for r in self.low_tree.get_children(): self.low_tree.delete(r)
        c.execute("""SELECT p.name, cat.name, p.stock, p.price
                     FROM products p JOIN categories cat ON p.category_id=cat.id
                     WHERE p.stock < 5 ORDER BY p.stock""")
        for row in c.fetchall():
            self.low_tree.insert("", "end", values=row, tags=("low",))
        self.low_tree.tag_configure("low", foreground="#e74c3c")

        for r in self.top_tree.get_children(): self.top_tree.delete(r)
        c.execute("""SELECT p.name, SUM(s.quantity), SUM(s.total)
                     FROM sales s JOIN products p ON s.product_id=p.id
                     GROUP BY p.id ORDER BY SUM(s.total) DESC LIMIT 10""")
        for row in c.fetchall():
            self.top_tree.insert("", "end",
                values=(row[0], row[1], f"₹{row[2]:,.2f}"))

        for r in self.cat_tree.get_children(): self.cat_tree.delete(r)
        c.execute("""SELECT cat.name, COUNT(s.id), SUM(s.total)
                     FROM sales s
                     JOIN products p ON s.product_id=p.id
                     JOIN categories cat ON p.category_id=cat.id
                     GROUP BY cat.id ORDER BY SUM(s.total) DESC""")
        for row in c.fetchall():
            self.cat_tree.insert("", "end",
                values=(row[0], row[1], f"₹{row[2]:,.2f}"))

        for r in self.cust_tree.get_children(): self.cust_tree.delete(r)
        c.execute("""SELECT COALESCE(cu.name,'Walk-in'), COUNT(s.id), SUM(s.total)
                     FROM sales s
                     LEFT JOIN customers cu ON s.customer_id=cu.id
                     GROUP BY s.customer_id ORDER BY SUM(s.total) DESC LIMIT 10""")
        for row in c.fetchall():
            self.cust_tree.insert("", "end",
                values=(row[0], row[1], f"₹{row[2]:,.2f}"))

        conn.close()


#  MAIN APPLICATION WINDOW

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("👔 Cloth Store Management System")
        self.geometry("1200x720")
        self.minsize(960, 620)
        self.configure(bg=DARK_BG)

        self._build_sidebar()
        self._build_content()
        self.show_page("Dashboard")

    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=CARD_BG, width=190)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(sidebar, bg=ACCENT, pady=18)
        logo_frame.pack(fill="x")
        tk.Label(logo_frame, text="👔", bg=ACCENT,
                 font=("Segoe UI", 28)).pack()
        tk.Label(logo_frame, text="CLOTH STORE", bg=ACCENT,
                 fg="white", font=("Segoe UI", 11, "bold")).pack()
        tk.Label(logo_frame, text="Management System", bg=ACCENT,
                 fg="#f8d7da", font=("Segoe UI", 8)).pack()

        tk.Frame(sidebar, bg=ACCENT, height=2).pack(fill="x")

        nav_items = [
            ("📊", "Dashboard"),
            ("🧵", "Products"),
            ("👥", "Customers"),
            ("🛒", "Sales"),
            ("🏷", "Categories"),
            ("📈", "Reports"),
        ]
        self.nav_buttons = {}
        for icon, name in nav_items:
            btn = tk.Button(
                sidebar, text=f"  {icon}  {name}",
                command=lambda n=name: self.show_page(n),
                bg=CARD_BG, fg=TEXT_MAIN, activebackground=ACCENT,
                activeforeground="white", font=("Segoe UI", 11),
                anchor="w", relief="flat", pady=11, cursor="hand2"
            )
            btn.pack(fill="x", padx=0)
            self.nav_buttons[name] = btn

        # Bottom info
        tk.Frame(sidebar, bg=ACCENT, height=1).pack(fill="x", side="bottom", pady=(0,0))
        tk.Label(sidebar, text="SQLite  ·  Python Turtle",
                 bg=CARD_BG, fg=TEXT_SUB, font=("Segoe UI", 8)).pack(side="bottom", pady=4)

    def _build_content(self):
        self.content = tk.Frame(self, bg=DARK_BG)
        self.content.pack(side="right", fill="both", expand=True)

        self.pages = {}
        for PageClass, name in [
            (DashboardPage,  "Dashboard"),
            (ProductsPage,   "Products"),
            (CustomersPage,  "Customers"),
            (SalesPage,      "Sales"),
            (CategoriesPage, "Categories"),
            (ReportsPage,    "Reports"),
        ]:
            page = PageClass(self.content, self)
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.pages[name] = page

    def show_page(self, name):
        for n, btn in self.nav_buttons.items():
            btn.configure(bg=ACCENT if n == name else CARD_BG,
                          fg="white" if n == name else TEXT_MAIN)
        self.pages[name].tkraise()
        if hasattr(self.pages[name], "load_products"):
            self.pages[name].load_products()
        if hasattr(self.pages[name], "load_customers"):
            self.pages[name].load_customers()
        if hasattr(self.pages[name], "load_sales"):
            self.pages[name].load_sales()
        if hasattr(self.pages[name], "load_reports"):
            self.pages[name].load_reports()
        if hasattr(self.pages[name], "load_categories"):
            self.pages[name].load_categories()
        if hasattr(self.pages[name], "_load_combos"):
            self.pages[name]._load_combos()

    def refresh_dashboard(self):
        self.pages["Dashboard"].refresh()


#  ENTRY POINT

if __name__ == "__main__":
    # 1. Turtle splash screen
    try:
        draw_splash()
    except Exception:
        pass   # headless / CI environments

    # 2. Initialize database
    init_db()

    # 3. Launch main Tkinter app
    app = App()
    app.mainloop()
