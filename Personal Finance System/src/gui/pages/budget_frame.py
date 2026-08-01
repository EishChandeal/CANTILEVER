import datetime
from tkinter import messagebox
import customtkinter

from src.gui.pages.base_frame import BaseFrame
from src.config import PALETTE
from src.utils.helpers import format_currency

class SetBudgetDialog(customtkinter.CTkToplevel):
    """Modal dialog for creating or updating a monthly category budget."""

    def __init__(self, parent, title: str, categories: list[dict], month: int, year: int, initial_data: dict = None, on_save=None):
        super().__init__(parent)

        self.title(title)
        self.geometry("400x320")
        self.resizable(False, False)
        self.on_save = on_save
        self.month = month
        self.year = year
        self.categories = [c for c in categories if c["type"] == "expense"]

        self.transient(parent)
        self.grab_set()

        self.configure(fg_color=PALETTE["CARD"])

        # Title
        hdr = customtkinter.CTkLabel(
            self,
            text=title,
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        hdr.pack(padx=20, pady=(20, 15), anchor="w")

        # Category Option
        cat_lbl = customtkinter.CTkLabel(self, text="Expense Category", font=customtkinter.CTkFont(size=12, weight="bold"), text_color=PALETTE["SUBTEXT"])
        cat_lbl.pack(padx=20, anchor="w")

        cat_names = [c["name"] for c in self.categories] if self.categories else ["No expense categories"]
        self.cat_opt = customtkinter.CTkOptionMenu(self, values=cat_names)
        self.cat_opt.pack(padx=20, pady=(2, 15), fill="x")

        if initial_data and "category_name" in initial_data:
            self.cat_opt.set(initial_data["category_name"])

        # Limit Entry
        limit_lbl = customtkinter.CTkLabel(self, text="Monthly Budget Limit (₹)", font=customtkinter.CTkFont(size=12, weight="bold"), text_color=PALETTE["SUBTEXT"])
        limit_lbl.pack(padx=20, anchor="w")

        self.limit_entry = customtkinter.CTkEntry(self, placeholder_text="e.g. 15000")
        if initial_data and "budget" in initial_data:
            self.limit_entry.insert(0, str(initial_data["budget"]))
        self.limit_entry.pack(padx=20, pady=(2, 20), fill="x")

        # Buttons
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
            text="Save Budget",
            fg_color=PALETTE["ACCENT"],
            command=self._on_save
        )
        save_btn.pack(side="right", expand=True, padx=(5, 0), fill="x")

    def _on_save(self):
        sel_cat_name = self.cat_opt.get()
        limit_str = self.limit_entry.get().strip()

        matching_cat = next((c for c in self.categories if c["name"] == sel_cat_name), None)
        if not matching_cat:
            messagebox.showerror("Invalid Category", "Please select a valid expense category.", parent=self)
            return

        try:
            limit = float(limit_str)
            if limit <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a positive numeric budget limit.", parent=self)
            return

        if self.on_save:
            self.on_save(matching_cat["id"], limit)
        self.destroy()


class BudgetFrame(BaseFrame):
    """Budget Manager page displaying monthly category budget progress cards."""

    MONTHS = [("Jan", 1), ("Feb", 2), ("Mar", 3), ("Apr", 4),
              ("May", 5), ("Jun", 6), ("Jul", 7), ("Aug", 8),
              ("Sep", 9), ("Oct", 10), ("Nov", 11), ("Dec", 12)]

    def __init__(self, parent, db_manager, services: dict):
        super().__init__(parent, db_manager, services)
        self.budget_service = services["budget"]
        self.settings_service = services["settings"]

        self.current_year = datetime.date.today().year
        self.current_month = datetime.date.today().month

        self.grid_columnconfigure(0, weight=1)

        # 1. Header Toolbar
        self.toolbar = customtkinter.CTkFrame(self, fg_color=PALETTE["CARD"], corner_radius=10)
        self.toolbar.pack(padx=20, pady=(15, 15), fill="x")

        title_label = customtkinter.CTkLabel(
            self.toolbar,
            text="🎯 Budget Limits",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        title_label.pack(side="left", padx=15, pady=12)

        # Month Filter
        month_labels = [m[0] for m in self.MONTHS]
        self.month_opt = customtkinter.CTkOptionMenu(
            self.toolbar,
            values=month_labels,
            width=100,
            command=lambda _: self.refresh()
        )
        cur_m_name = self.MONTHS[self.current_month - 1][0]
        self.month_opt.set(cur_m_name)
        self.month_opt.pack(side="left", padx=6, pady=12)

        # Year Filter
        year_options = [str(y) for y in range(self.current_year - 2, self.current_year + 3)]
        self.year_opt = customtkinter.CTkOptionMenu(
            self.toolbar,
            values=year_options,
            width=90,
            command=lambda _: self.refresh()
        )
        self.year_opt.set(str(self.current_year))
        self.year_opt.pack(side="left", padx=6, pady=12)

        # Add Budget Button
        add_btn = customtkinter.CTkButton(
            self.toolbar,
            text="＋ Set Budget",
            fg_color=PALETTE["ACCENT"],
            command=self._open_add_dialog
        )
        add_btn.pack(side="right", padx=15, pady=12)

        # 2. Cards Grid Container
        self.cards_container = customtkinter.CTkFrame(self, fg_color="transparent")
        self.cards_container.pack(padx=20, pady=(0, 20), fill="both", expand=True)

    def refresh(self):
        """Fetches budget comparison data for selected month/year and renders cards grid."""
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        sel_m_name = self.month_opt.get()
        month_int = next((m[1] for m in self.MONTHS if m[0] == sel_m_name), self.current_month)
        
        try:
            year_int = int(self.year_opt.get())
        except ValueError:
            year_int = self.current_year

        budgets = self.budget_service.get_budget_vs_actual(month_int, year_int)
        symbol = self.settings_service.get_currency_symbol()

        if not budgets:
            empty_box = customtkinter.CTkFrame(self.cards_container, fg_color=PALETTE["CARD"], corner_radius=10)
            empty_box.pack(padx=20, pady=40, fill="x")
            
            empty_lbl = customtkinter.CTkLabel(
                empty_box,
                text=f"No budgets set for {sel_m_name} {year_int}.\nClick '＋ Set Budget' above to configure limits.",
                font=customtkinter.CTkFont(size=14),
                text_color=PALETTE["SUBTEXT"]
            )
            empty_lbl.pack(pady=30)
            return

        # Render 2-column Grid
        self.cards_container.grid_columnconfigure((0, 1), weight=1, uniform="bcard")

        for idx, b in enumerate(budgets):
            row = idx // 2
            col = idx % 2

            card = customtkinter.CTkFrame(self.cards_container, fg_color=PALETTE["CARD"], corner_radius=10)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            # Header inside Card
            hdr_frame = customtkinter.CTkFrame(card, fg_color="transparent")
            hdr_frame.pack(padx=15, pady=(12, 4), fill="x")

            cat_dot_lbl = customtkinter.CTkLabel(
                hdr_frame,
                text=f"● {b['category_name']}",
                font=customtkinter.CTkFont(size=14, weight="bold"),
                text_color=b["color"]
            )
            cat_dot_lbl.pack(side="left", anchor="w")

            pct_lbl = customtkinter.CTkLabel(
                hdr_frame,
                text=f"{b['percent_used']}%",
                font=customtkinter.CTkFont(size=13, weight="bold"),
                text_color=PALETTE["DANGER"] if b["percent_used"] >= 90 else (PALETTE["WARNING"] if b["percent_used"] >= 70 else PALETTE["SUCCESS"])
            )
            pct_lbl.pack(side="right", anchor="e")

            # Progress Bar
            ratio = min(b["spent"] / b["budget"], 1.0) if b["budget"] > 0 else 0.0
            if ratio >= 0.90:
                p_color = PALETTE["DANGER"]
            elif ratio >= 0.70:
                p_color = PALETTE["WARNING"]
            else:
                p_color = PALETTE["SUCCESS"]

            pbar = customtkinter.CTkProgressBar(card, height=10, progress_color=p_color)
            pbar.set(ratio)
            pbar.pack(padx=15, pady=6, fill="x")

            # Spent vs Limit Label
            info_lbl = customtkinter.CTkLabel(
                card,
                text=f"{format_currency(b['spent'], symbol)} spent of {format_currency(b['budget'], symbol)} limit",
                font=customtkinter.CTkFont(size=11),
                text_color=PALETTE["SUBTEXT"]
            )
            info_lbl.pack(padx=15, pady=(0, 8), anchor="w")

            # Action Buttons Row
            btn_frame = customtkinter.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(padx=15, pady=(0, 12), fill="x")

            edit_btn = customtkinter.CTkButton(
                btn_frame,
                text="✏️ Edit",
                width=70,
                height=26,
                fg_color="transparent",
                border_width=1,
                text_color=PALETTE["TEXT"],
                command=lambda data=b: self._open_edit_dialog(data)
            )
            edit_btn.pack(side="left", padx=(0, 5))

            del_btn = customtkinter.CTkButton(
                btn_frame,
                text="🗑️ Delete",
                width=70,
                height=26,
                fg_color="transparent",
                border_width=1,
                text_color=PALETTE["DANGER"],
                command=lambda b_id=b["id"]: self._delete_budget(b_id)
            )
            del_btn.pack(side="left", padx=5)

    def _open_add_dialog(self):
        categories = self.settings_service.get_all_categories()
        sel_m_name = self.month_opt.get()
        month_int = next((m[1] for m in self.MONTHS if m[0] == sel_m_name), self.current_month)
        year_int = int(self.year_opt.get())

        def on_save(cat_id, limit):
            self.budget_service.set_budget(cat_id, month_int, year_int, limit)
            self.refresh()

        SetBudgetDialog(
            parent=self.winfo_toplevel(),
            title=f"Set Budget for {sel_m_name} {year_int}",
            categories=categories,
            month=month_int,
            year=year_int,
            on_save=on_save
        )

    def _open_edit_dialog(self, b_data: dict):
        categories = self.settings_service.get_all_categories()
        sel_m_name = self.month_opt.get()
        month_int = next((m[1] for m in self.MONTHS if m[0] == sel_m_name), self.current_month)
        year_int = int(self.year_opt.get())

        def on_save(cat_id, limit):
            self.budget_service.set_budget(cat_id, month_int, year_int, limit)
            self.refresh()

        SetBudgetDialog(
            parent=self.winfo_toplevel(),
            title="Edit Category Budget",
            categories=categories,
            month=month_int,
            year=year_int,
            initial_data=b_data,
            on_save=on_save
        )

    def _delete_budget(self, budget_id: int):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to remove this budget limit?", parent=self.winfo_toplevel())
        if confirm:
            self.budget_service.budget_dao.delete(budget_id)
            self.refresh()
