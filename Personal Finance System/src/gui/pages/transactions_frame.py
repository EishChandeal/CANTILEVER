import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter

from src.gui.pages.base_frame import BaseFrame
from src.config import PALETTE
from src.utils.helpers import format_currency, format_date

class TransactionDialog(customtkinter.CTkToplevel):
    """Modal dialog for adding or editing a transaction."""

    def __init__(self, parent, title: str, categories: list[dict], initial_data: dict = None, on_save=None):
        super().__init__(parent)

        self.title(title)
        self.geometry("450x520")
        self.resizable(False, False)
        self.on_save = on_save
        self.initial_data = initial_data
        self.all_categories = categories

        # Modal window configuration
        self.transient(parent)
        self.grab_set()

        # Layout
        self.configure(fg_color=PALETTE["CARD"])
        self.grid_columnconfigure(0, weight=1)

        # Title Header
        title_label = customtkinter.CTkLabel(
            self,
            text=title,
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        title_label.pack(padx=20, pady=(20, 15), anchor="w")

        # 1. Type Selector (Income / Expense)
        type_label = customtkinter.CTkLabel(self, text="Type", font=customtkinter.CTkFont(size=12, weight="bold"), text_color=PALETTE["SUBTEXT"])
        type_label.pack(padx=20, anchor="w")

        default_type = initial_data.get("type", "expense") if initial_data else "expense"
        self.type_seg = customtkinter.CTkSegmentedButton(
            self,
            values=["Income", "Expense"],
            command=self._on_type_change,
            selected_color=PALETTE["ACCENT"]
        )
        self.type_seg.set(default_type.capitalize())
        self.type_seg.pack(padx=20, pady=(2, 12), fill="x")

        # 2. Category Dropdown
        cat_label = customtkinter.CTkLabel(self, text="Category", font=customtkinter.CTkFont(size=12, weight="bold"), text_color=PALETTE["SUBTEXT"])
        cat_label.pack(padx=20, anchor="w")

        self.category_opt = customtkinter.CTkOptionMenu(self, values=["Select Category"])
        self.category_opt.pack(padx=20, pady=(2, 12), fill="x")

        # 3. Amount Entry
        amt_label = customtkinter.CTkLabel(self, text="Amount (₹)", font=customtkinter.CTkFont(size=12, weight="bold"), text_color=PALETTE["SUBTEXT"])
        amt_label.pack(padx=20, anchor="w")

        self.amount_entry = customtkinter.CTkEntry(self, placeholder_text="0.00")
        if initial_data and "amount" in initial_data:
            self.amount_entry.insert(0, str(initial_data["amount"]))
        self.amount_entry.pack(padx=20, pady=(2, 12), fill="x")

        # 4. Description Entry
        desc_label = customtkinter.CTkLabel(self, text="Description", font=customtkinter.CTkFont(size=12, weight="bold"), text_color=PALETTE["SUBTEXT"])
        desc_label.pack(padx=20, anchor="w")

        self.desc_entry = customtkinter.CTkEntry(self, placeholder_text="Enter details...")
        if initial_data and "description" in initial_data:
            self.desc_entry.insert(0, initial_data.get("description", ""))
        self.desc_entry.pack(padx=20, pady=(2, 12), fill="x")

        # 5. Date Entry
        date_label = customtkinter.CTkLabel(self, text="Date (YYYY-MM-DD)", font=customtkinter.CTkFont(size=12, weight="bold"), text_color=PALETTE["SUBTEXT"])
        date_label.pack(padx=20, anchor="w")

        default_date = initial_data.get("date", datetime.date.today().strftime("%Y-%m-%d")) if initial_data else datetime.date.today().strftime("%Y-%m-%d")
        self.date_entry = customtkinter.CTkEntry(self, placeholder_text="YYYY-MM-DD")
        self.date_entry.insert(0, default_date)
        self.date_entry.pack(padx=20, pady=(2, 20), fill="x")

        # Buttons (Save / Cancel)
        btn_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(padx=20, pady=(0, 20), fill="x")

        cancel_btn = customtkinter.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="transparent",
            border_width=1,
            text_color=PALETTE["TEXT"],
            command=self.destroy
        )
        cancel_btn.pack(side="left", expand=True, padx=(0, 5), fill="x")

        save_btn = customtkinter.CTkButton(
            btn_frame,
            text="Save Transaction",
            fg_color=PALETTE["ACCENT"],
            command=self._on_save
        )
        save_btn.pack(side="right", expand=True, padx=(5, 0), fill="x")

        # Populate categories for initial type
        self._on_type_change(self.type_seg.get())
        if initial_data and "category_name" in initial_data:
            self.category_opt.set(initial_data["category_name"])

    def _on_type_change(self, selected_type_str: str):
        type_lower = selected_type_str.lower()
        matching_cats = [c["name"] for c in self.all_categories if c["type"] == type_lower]
        
        if matching_cats:
            self.category_opt.configure(values=matching_cats)
            self.category_opt.set(matching_cats[0])
        else:
            self.category_opt.configure(values=["No categories"])
            self.category_opt.set("No categories")

    def _on_save(self):
        sel_type = self.type_seg.get().lower()
        sel_cat_name = self.category_opt.get()
        amount_str = self.amount_entry.get().strip()
        desc = self.desc_entry.get().strip()
        date_str = self.date_entry.get().strip()

        # Validation
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive number for amount.", parent=self)
            return

        matching_cat = next((c for c in self.all_categories if c["name"] == sel_cat_name), None)
        if not matching_cat:
            messagebox.showerror("Invalid Category", "Please select a valid category.", parent=self)
            return

        try:
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Date must be in YYYY-MM-DD format.", parent=self)
            return

        data = {
            "category_id": matching_cat["id"],
            "type": sel_type,
            "amount": amount,
            "description": desc,
            "date": date_str
        }

        if self.on_save:
            self.on_save(data)
        self.destroy()


class TransactionsFrame(BaseFrame):
    """Transactions management page with filtering, summary strip, and Treeview table."""

    MONTHS = [("All Months", None), ("Jan", 1), ("Feb", 2), ("Mar", 3), ("Apr", 4),
              ("May", 5), ("Jun", 6), ("Jul", 7), ("Aug", 8), ("Sep", 9),
              ("Oct", 10), ("Nov", 11), ("Dec", 12)]

    def __init__(self, parent, db_manager, services: dict):
        super().__init__(parent, db_manager, services)
        self.finance_service = services["finance"]
        self.settings_service = services["settings"]

        self.current_year = datetime.date.today().year
        self.current_month = datetime.date.today().month

        # Layout Container
        self.grid_columnconfigure(0, weight=1)

        # 1. Filter Bar (Top)
        self.filter_frame = customtkinter.CTkFrame(self, fg_color=PALETTE["CARD"], corner_radius=10)
        self.filter_frame.pack(padx=20, pady=(15, 10), fill="x")

        # Type Filter Segmented Button
        self.type_filter = customtkinter.CTkSegmentedButton(
            self.filter_frame,
            values=["All", "Income", "Expense"],
            command=lambda _: self.refresh()
        )
        self.type_filter.set("All")
        self.type_filter.pack(side="left", padx=12, pady=12)

        # Month Filter Dropdown
        month_labels = [m[0] for m in self.MONTHS]
        self.month_opt = customtkinter.CTkOptionMenu(
            self.filter_frame,
            values=month_labels,
            width=110,
            command=lambda _: self.refresh()
        )
        # Default to current month name
        cur_month_label = self.MONTHS[self.current_month][0]
        self.month_opt.set(cur_month_label)
        self.month_opt.pack(side="left", padx=6, pady=12)

        # Year Filter Dropdown
        year_options = [str(y) for y in range(self.current_year - 3, self.current_year + 3)]
        self.year_opt = customtkinter.CTkOptionMenu(
            self.filter_frame,
            values=year_options,
            width=90,
            command=lambda _: self.refresh()
        )
        self.year_opt.set(str(self.current_year))
        self.year_opt.pack(side="left", padx=6, pady=12)

        # Search Bar Entry
        self.search_entry = customtkinter.CTkEntry(
            self.filter_frame,
            placeholder_text="🔍 Search description...",
            width=180
        )
        self.search_entry.pack(side="left", padx=6, pady=12)
        self.search_entry.bind("<KeyRelease>", lambda _: self.refresh())

        # Action Buttons (Right)
        add_income_btn = customtkinter.CTkButton(
            self.filter_frame,
            text="＋ Income",
            fg_color=PALETTE["SUCCESS"],
            hover_color="#16a34a",
            width=100,
            command=lambda: self._open_add_dialog("income")
        )
        add_income_btn.pack(side="right", padx=(4, 12), pady=12)

        add_expense_btn = customtkinter.CTkButton(
            self.filter_frame,
            text="＋ Expense",
            fg_color=PALETTE["DANGER"],
            hover_color="#dc2626",
            width=100,
            command=lambda: self._open_add_dialog("expense")
        )
        add_expense_btn.pack(side="right", padx=4, pady=12)

        # 2. Summary Strip Bar
        self.summary_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.summary_frame.pack(padx=20, pady=(0, 10), fill="x")

        self.summary_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="stat")

        # Stat Card 1: Income
        self.card_inc = customtkinter.CTkFrame(self.summary_frame, fg_color=PALETTE["CARD"], corner_radius=8)
        self.card_inc.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.inc_val_label = customtkinter.CTkLabel(self.card_inc, text="Income: ₹ 0.00", font=customtkinter.CTkFont(size=14, weight="bold"), text_color=PALETTE["SUCCESS"])
        self.inc_val_label.pack(pady=10)

        # Stat Card 2: Expenses
        self.card_exp = customtkinter.CTkFrame(self.summary_frame, fg_color=PALETTE["CARD"], corner_radius=8)
        self.card_exp.grid(row=0, column=1, padx=4, sticky="ew")
        self.exp_val_label = customtkinter.CTkLabel(self.card_exp, text="Expenses: ₹ 0.00", font=customtkinter.CTkFont(size=14, weight="bold"), text_color=PALETTE["DANGER"])
        self.exp_val_label.pack(pady=10)

        # Stat Card 3: Net
        self.card_net = customtkinter.CTkFrame(self.summary_frame, fg_color=PALETTE["CARD"], corner_radius=8)
        self.card_net.grid(row=0, column=2, padx=(8, 0), sticky="ew")
        self.net_val_label = customtkinter.CTkLabel(self.card_net, text="Net: ₹ 0.00", font=customtkinter.CTkFont(size=14, weight="bold"), text_color=PALETTE["ACCENT"])
        self.net_val_label.pack(pady=10)

        # 3. Transactions Table (ttk.Treeview inside CTkFrame container)
        self.table_container = customtkinter.CTkFrame(self, fg_color=PALETTE["CARD"], corner_radius=10)
        self.table_container.pack(padx=20, pady=(0, 15), fill="both", expand=True)

        # Configure Dark Theme for ttk.Treeview
        self._style_treeview()

        columns = ("date", "type", "category", "description", "amount")
        self.tree = ttk.Treeview(
            self.table_container,
            columns=columns,
            show="headings",
            height=14,
            selectmode="browse"
        )

        self.tree.heading("date", text="Date")
        self.tree.heading("type", text="Type")
        self.tree.heading("category", text="Category")
        self.tree.heading("description", text="Description")
        self.tree.heading("amount", text="Amount")

        self.tree.column("date", width=120, anchor="center")
        self.tree.column("type", width=90, anchor="center")
        self.tree.column("category", width=140, anchor="w")
        self.tree.column("description", width=300, anchor="w")
        self.tree.column("amount", width=140, anchor="e")

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(self.table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Context Menu (Right Click)
        self.context_menu = tk.Menu(self, tearoff=0, bg=PALETTE["SIDEBAR"], fg=PALETTE["TEXT"], activebackground=PALETTE["ACCENT"])
        self.context_menu.add_command(label="✏️  Edit Transaction", command=self._edit_selected)
        self.context_menu.add_command(label="🗑️  Delete Transaction", command=self._delete_selected)

        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Double-1>", lambda _: self._edit_selected())

        # Internal dataset map (iid -> row_dict)
        self.rows_map = {}

    def _style_treeview(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Treeview",
                        background=PALETTE["CARD"],
                        foreground=PALETTE["TEXT"],
                        fieldbackground=PALETTE["CARD"],
                        bordercolor=PALETTE["CARD"],
                        rowheight=32,
                        font=("Segoe UI", 10))

        style.configure("Treeview.Heading",
                        background=PALETTE["SIDEBAR"],
                        foreground=PALETTE["TEXT"],
                        relief="flat",
                        font=("Segoe UI", 10, "bold"))

        style.map("Treeview",
                  background=[("selected", PALETTE["ACCENT"])],
                  foreground=[("selected", "#ffffff")])

    def refresh(self):
        """Fetches transactions based on current filters and updates summary strip & table."""
        # 1. Parse Filters
        type_str = self.type_filter.get().lower()
        if type_str == "all":
            type_str = None

        selected_m_label = self.month_opt.get()
        month_int = next((m[1] for m in self.MONTHS if m[0] == selected_m_label), None)

        try:
            year_int = int(self.year_opt.get())
        except ValueError:
            year_int = self.current_year

        search_query = self.search_entry.get().strip().lower()

        # 2. Fetch Data from Service
        transactions = self.finance_service.get_transactions(
            month=month_int,
            year=year_int,
            type_=type_str
        )

        # Search query filtering
        if search_query:
            transactions = [
                t for t in transactions
                if search_query in (t.get("description") or "").lower()
                or search_query in (t.get("category_name") or "").lower()
            ]

        # 3. Calculate Summary Totals
        symbol = self.settings_service.get_currency_symbol()
        total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
        total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
        net = total_income - total_expense

        self.inc_val_label.configure(text=f"Income: {format_currency(total_income, symbol)}")
        self.exp_val_label.configure(text=f"Expenses: {format_currency(total_expense, symbol)}")
        
        net_prefix = "+" if net > 0 else ""
        self.net_val_label.configure(
            text=f"Net: {net_prefix}{format_currency(net, symbol)}",
            text_color=PALETTE["SUCCESS"] if net >= 0 else PALETTE["DANGER"]
        )

        # 4. Populate Table
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.rows_map.clear()

        # Set up tag colors
        self.tree.tag_configure("income_row", foreground=PALETTE["SUCCESS"])
        self.tree.tag_configure("expense_row", foreground=PALETTE["DANGER"])

        for index, t in enumerate(transactions):
            iid = str(t["id"])
            self.rows_map[iid] = t

            amt_formatted = format_currency(t["amount"], symbol)
            type_display = t["type"].capitalize()
            cat_display = t.get("category_name") or "Uncategorized"
            desc_display = t.get("description") or "-"
            date_display = format_date(t["date"])

            row_tag = "income_row" if t["type"] == "income" else "expense_row"

            self.tree.insert(
                "",
                "end",
                iid=iid,
                values=(date_display, type_display, cat_display, desc_display, amt_formatted),
                tags=(row_tag,)
            )

    def _open_add_dialog(self, default_type: str):
        categories = self.settings_service.get_all_categories()

        def on_save(data):
            self.finance_service.add_transaction(
                category_id=data["category_id"],
                type_=data["type"],
                amount=data["amount"],
                description=data["description"],
                date=data["date"]
            )
            self.refresh()

        TransactionDialog(
            parent=self.winfo_toplevel(),
            title=f"Add {default_type.capitalize()}",
            categories=categories,
            initial_data={"type": default_type},
            on_save=on_save
        )

    def _show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def _edit_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        iid = selected_items[0]
        row_data = self.rows_map.get(iid)
        if not row_data:
            return

        categories = self.settings_service.get_all_categories()

        def on_save(data):
            self.finance_service.update_transaction(
                transaction_id=row_data["id"],
                category_id=data["category_id"],
                type=data["type"],
                amount=data["amount"],
                description=data["description"],
                date=data["date"]
            )
            self.refresh()

        TransactionDialog(
            parent=self.winfo_toplevel(),
            title="Edit Transaction",
            categories=categories,
            initial_data=row_data,
            on_save=on_save
        )

    def _delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        iid = selected_items[0]
        row_data = self.rows_map.get(iid)
        if not row_data:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete transaction:\n'{row_data.get('description', 'Transaction')}' ({format_currency(row_data['amount'])})?",
            parent=self.winfo_toplevel()
        )
        if confirm:
            self.finance_service.delete_transaction(row_data["id"])
            self.refresh()
