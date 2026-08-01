import csv
import os
import datetime
from tkinter import filedialog, messagebox
import customtkinter

from src.gui.pages.base_frame import BaseFrame
from src.config import PALETTE, DB_PATH

PRESET_COLORS = [
    ("#ef4444", "Red"),
    ("#f97316", "Orange"),
    ("#eab308", "Yellow"),
    ("#22c55e", "Green"),
    ("#14b8a6", "Teal"),
    ("#3b82f6", "Blue"),
    ("#8b5cf6", "Purple"),
    ("#ec4899", "Pink"),
]

CURRENCY_OPTIONS = {
    "INR ₹": ("INR", "₹"),
    "USD $": ("USD", "$"),
    "EUR €": ("EUR", "€"),
    "GBP £": ("GBP", "£"),
}


class AddCategoryDialog(customtkinter.CTkToplevel):
    """Modal dialog for adding a new income or expense category."""

    def __init__(self, parent, category_type: str, on_save=None):
        super().__init__(parent)

        self.title(f"Add {category_type.capitalize()} Category")
        self.geometry("380x320")
        self.resizable(False, False)
        self.on_save = on_save
        self.category_type = category_type
        self.selected_color = PRESET_COLORS[0][0]

        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=PALETTE["CARD"])

        # Title
        hdr = customtkinter.CTkLabel(
            self,
            text=f"＋ Add {category_type.capitalize()} Category",
            font=customtkinter.CTkFont(size=17, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        hdr.pack(padx=20, pady=(20, 15), anchor="w")

        # Name Entry
        name_lbl = customtkinter.CTkLabel(self, text="Category Name", font=customtkinter.CTkFont(size=12, weight="bold"), text_color=PALETTE["SUBTEXT"])
        name_lbl.pack(padx=20, anchor="w")
        self.name_entry = customtkinter.CTkEntry(self, placeholder_text="e.g. Groceries, Bonus...")
        self.name_entry.pack(padx=20, pady=(2, 14), fill="x")

        # Color Picker (Swatches)
        color_lbl = customtkinter.CTkLabel(self, text="Color", font=customtkinter.CTkFont(size=12, weight="bold"), text_color=PALETTE["SUBTEXT"])
        color_lbl.pack(padx=20, anchor="w")

        self.color_swatch_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.color_swatch_frame.pack(padx=20, pady=(4, 14), anchor="w")

        self.swatch_btns = []
        for hex_color, name in PRESET_COLORS:
            btn = customtkinter.CTkButton(
                self.color_swatch_frame,
                text="",
                width=28,
                height=28,
                corner_radius=14,
                fg_color=hex_color,
                hover_color=hex_color,
                border_width=2,
                border_color="transparent",
                command=lambda c=hex_color: self._select_color(c)
            )
            btn.pack(side="left", padx=3)
            self.swatch_btns.append((btn, hex_color))

        # Highlight default color
        self._select_color(PRESET_COLORS[0][0])

        # Buttons
        btn_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(padx=20, pady=(0, 20), fill="x", side="bottom")

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
            text="Save Category",
            fg_color=PALETTE["ACCENT"],
            command=self._on_save
        )
        save_btn.pack(side="right", expand=True, padx=(5, 0), fill="x")

    def _select_color(self, selected_hex: str):
        self.selected_color = selected_hex
        for btn, hex_color in self.swatch_btns:
            if hex_color == selected_hex:
                btn.configure(border_color=PALETTE["TEXT"])
            else:
                btn.configure(border_color="transparent")

    def _on_save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Invalid Name", "Please enter a category name.", parent=self)
            return
        if self.on_save:
            self.on_save(name, self.category_type, self.selected_color)
        self.destroy()


class SettingsFrame(BaseFrame):
    """Settings page with General, Categories, and Data Management tabs."""

    def __init__(self, parent, db_manager, services: dict):
        super().__init__(parent, db_manager, services)
        self.settings_service = services["settings"]
        self.finance_service = services["finance"]

        self.grid_columnconfigure(0, weight=1)

        # CTkTabview
        self.tabs = customtkinter.CTkTabview(
            self,
            fg_color=PALETTE["CARD"],
            segmented_button_fg_color=PALETTE["SIDEBAR"],
            segmented_button_selected_color=PALETTE["ACCENT"],
            segmented_button_selected_hover_color=PALETTE["ACCENT"],
            segmented_button_unselected_color=PALETTE["SIDEBAR"],
            text_color=PALETTE["TEXT"]
        )
        self.tabs.pack(padx=20, pady=15, fill="both", expand=True)

        self.tabs.add("⚙️  General")
        self.tabs.add("🏷️  Categories")
        self.tabs.add("💾  Data")

        self._build_general_tab()
        self._build_categories_tab()
        self._build_data_tab()

    # ── Tab 1: General ───────────────────────────────────────────────────────

    def _build_general_tab(self):
        tab = self.tabs.tab("⚙️  General")
        tab.configure(fg_color="transparent")

        # Currency Section
        section1 = customtkinter.CTkFrame(tab, fg_color=PALETTE["SIDEBAR"], corner_radius=10)
        section1.pack(padx=10, pady=(15, 10), fill="x")

        currency_ttl = customtkinter.CTkLabel(
            section1,
            text="💱  Currency",
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        currency_ttl.pack(padx=15, pady=(14, 5), anchor="w")

        currency_sub = customtkinter.CTkLabel(
            section1,
            text="Select the currency symbol displayed throughout the app.",
            font=customtkinter.CTkFont(size=11),
            text_color=PALETTE["SUBTEXT"]
        )
        currency_sub.pack(padx=15, pady=(0, 8), anchor="w")

        curr_row = customtkinter.CTkFrame(section1, fg_color="transparent")
        curr_row.pack(padx=15, pady=(0, 10), fill="x")

        # Read saved currency
        saved_code = self.settings_service.get("currency_code", "INR")
        saved_symbol = self.settings_service.get("currency_symbol", "₹")
        default_key = next(
            (k for k, (code, sym) in CURRENCY_OPTIONS.items() if code == saved_code),
            "INR ₹"
        )

        self.currency_opt = customtkinter.CTkOptionMenu(
            curr_row,
            values=list(CURRENCY_OPTIONS.keys()),
            command=self._on_currency_change,
            width=160
        )
        self.currency_opt.set(default_key)
        self.currency_opt.pack(side="left", anchor="w")

        # Toast Label
        self.currency_toast = customtkinter.CTkLabel(
            section1,
            text="",
            font=customtkinter.CTkFont(size=11),
            text_color=PALETTE["WARNING"]
        )
        self.currency_toast.pack(padx=15, pady=(0, 14), anchor="w")

        # Appearance Section
        section2 = customtkinter.CTkFrame(tab, fg_color=PALETTE["SIDEBAR"], corner_radius=10)
        section2.pack(padx=10, pady=10, fill="x")

        appearance_ttl = customtkinter.CTkLabel(
            section2,
            text="🎨  Appearance",
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        appearance_ttl.pack(padx=15, pady=(14, 5), anchor="w")

        appearance_sub = customtkinter.CTkLabel(
            section2,
            text="Toggle between Dark and Light mode. Applied immediately.",
            font=customtkinter.CTkFont(size=11),
            text_color=PALETTE["SUBTEXT"]
        )
        appearance_sub.pack(padx=15, pady=(0, 8), anchor="w")

        saved_theme = self.settings_service.get("theme", "dark")
        self.theme_seg = customtkinter.CTkSegmentedButton(
            section2,
            values=["Dark", "Light"],
            command=self._on_theme_change,
            selected_color=PALETTE["ACCENT"],
            width=200
        )
        self.theme_seg.set(saved_theme.capitalize())
        self.theme_seg.pack(padx=15, pady=(0, 14), anchor="w")

    def _on_currency_change(self, selected: str):
        code, symbol = CURRENCY_OPTIONS.get(selected, ("INR", "₹"))
        self.settings_service.set("currency_code", code)
        self.settings_service.set("currency_symbol", symbol)
        self.currency_toast.configure(text="ℹ️  Restart the app to apply the currency change globally.")
        # Auto-hide toast after 4 seconds
        self.after(4000, lambda: self.currency_toast.configure(text=""))

    def _on_theme_change(self, selected: str):
        mode = selected.lower()
        customtkinter.set_appearance_mode(mode)
        self.settings_service.set("theme", mode)

    # ── Tab 2: Categories ────────────────────────────────────────────────────

    def _build_categories_tab(self):
        tab = self.tabs.tab("🏷️  Categories")
        tab.configure(fg_color="transparent")

        self.cat_tab_frame = tab
        self._render_categories()

    def _render_categories(self):
        for widget in self.cat_tab_frame.winfo_children():
            widget.destroy()

        all_cats = self.settings_service.get_all_categories()
        income_cats = [c for c in all_cats if c["type"] == "income"]
        expense_cats = [c for c in all_cats if c["type"] == "expense"]

        outer = customtkinter.CTkFrame(self.cat_tab_frame, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=10, pady=10)
        outer.grid_columnconfigure((0, 1), weight=1, uniform="catcol")

        self._render_category_column(outer, "Income", income_cats, col=0)
        self._render_category_column(outer, "Expense", expense_cats, col=1)

    def _render_category_column(self, parent, col_type: str, categories: list, col: int):
        panel = customtkinter.CTkFrame(parent, fg_color=PALETTE["SIDEBAR"], corner_radius=10)
        panel.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")

        hdr_color = PALETTE["SUCCESS"] if col_type == "Income" else PALETTE["DANGER"]
        hdr = customtkinter.CTkLabel(
            panel,
            text=f"{'💚' if col_type == 'Income' else '🔴'}  {col_type} Categories",
            font=customtkinter.CTkFont(size=13, weight="bold"),
            text_color=hdr_color
        )
        hdr.pack(padx=12, pady=(12, 8), anchor="w")

        # Category Rows
        list_frame = customtkinter.CTkScrollableFrame(panel, fg_color="transparent", height=280)
        list_frame.pack(padx=12, pady=(0, 8), fill="both", expand=True)

        for cat in categories:
            row = customtkinter.CTkFrame(list_frame, fg_color="transparent")
            row.pack(fill="x", pady=3)

            dot_lbl = customtkinter.CTkLabel(
                row,
                text="●",
                font=customtkinter.CTkFont(size=14),
                text_color=cat["color"]
            )
            dot_lbl.pack(side="left", padx=(0, 6))

            name_lbl = customtkinter.CTkLabel(
                row,
                text=cat["name"],
                font=customtkinter.CTkFont(size=12),
                text_color=PALETTE["TEXT"]
            )
            name_lbl.pack(side="left", anchor="w")

            del_btn = customtkinter.CTkButton(
                row,
                text="🗑️",
                width=32,
                height=26,
                fg_color="transparent",
                border_width=1,
                text_color=PALETTE["DANGER"],
                command=lambda c_id=cat["id"], c_name=cat["name"]: self._delete_category(c_id, c_name)
            )
            del_btn.pack(side="right", padx=(4, 0))

        # Add Category Button
        add_btn = customtkinter.CTkButton(
            panel,
            text=f"＋ Add {col_type} Category",
            fg_color="transparent",
            border_width=1,
            text_color=PALETTE["TEXT"],
            command=lambda t=col_type.lower(): self._open_add_category_dialog(t)
        )
        add_btn.pack(padx=12, pady=(0, 12), fill="x")

    def _open_add_category_dialog(self, category_type: str):
        def on_save(name, cat_type, color):
            try:
                self.settings_service.add_category(name, cat_type, color)
                self._render_categories()
            except RuntimeError as e:
                messagebox.showerror("Error", str(e), parent=self.winfo_toplevel())

        AddCategoryDialog(
            parent=self.winfo_toplevel(),
            category_type=category_type,
            on_save=on_save
        )

    def _delete_category(self, cat_id: int, cat_name: str):
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete category '{cat_name}'?\n\nNote: This will fail if transactions exist for this category.",
            parent=self.winfo_toplevel()
        )
        if not confirm:
            return

        deleted = self.settings_service.delete_category(cat_id)
        if deleted:
            messagebox.showinfo("Deleted", f"Category '{cat_name}' has been removed.", parent=self.winfo_toplevel())
            self._render_categories()
        else:
            messagebox.showwarning(
                "Cannot Delete",
                f"'{cat_name}' cannot be deleted because it has associated transactions.\n\nDelete those transactions first.",
                parent=self.winfo_toplevel()
            )

    # ── Tab 3: Data Management ───────────────────────────────────────────────

    def _build_data_tab(self):
        tab = self.tabs.tab("💾  Data")
        tab.configure(fg_color="transparent")

        # Export CSV
        export_section = customtkinter.CTkFrame(tab, fg_color=PALETTE["SIDEBAR"], corner_radius=10)
        export_section.pack(padx=10, pady=(15, 10), fill="x")

        exp_lbl = customtkinter.CTkLabel(
            export_section,
            text="📥  Export Data",
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        exp_lbl.pack(padx=15, pady=(14, 4), anchor="w")

        exp_sub = customtkinter.CTkLabel(
            export_section,
            text="Export all transaction history to a CSV file.",
            font=customtkinter.CTkFont(size=11),
            text_color=PALETTE["SUBTEXT"]
        )
        exp_sub.pack(padx=15, pady=(0, 10), anchor="w")

        export_btn = customtkinter.CTkButton(
            export_section,
            text="📥  Export All Transactions (CSV)",
            fg_color=PALETTE["ACCENT"],
            command=self._export_csv
        )
        export_btn.pack(padx=15, pady=(0, 14), anchor="w")

        # Clear All Data
        danger_section = customtkinter.CTkFrame(tab, fg_color=PALETTE["SIDEBAR"], corner_radius=10)
        danger_section.pack(padx=10, pady=10, fill="x")

        danger_lbl = customtkinter.CTkLabel(
            danger_section,
            text="⚠️  Danger Zone",
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color=PALETTE["DANGER"]
        )
        danger_lbl.pack(padx=15, pady=(14, 4), anchor="w")

        danger_sub = customtkinter.CTkLabel(
            danger_section,
            text="This permanently deletes ALL transactions, budgets, and savings goals.\nCategories and settings will be preserved.",
            font=customtkinter.CTkFont(size=11),
            text_color=PALETTE["SUBTEXT"],
            justify="left"
        )
        danger_sub.pack(padx=15, pady=(0, 10), anchor="w")

        clear_btn = customtkinter.CTkButton(
            danger_section,
            text="🗑️  Clear All Data",
            fg_color=PALETTE["DANGER"],
            hover_color="#dc2626",
            command=self._clear_all_data
        )
        clear_btn.pack(padx=15, pady=(0, 14), anchor="w")

        # DB Info
        info_section = customtkinter.CTkFrame(tab, fg_color=PALETTE["SIDEBAR"], corner_radius=10)
        info_section.pack(padx=10, pady=10, fill="x")

        info_ttl = customtkinter.CTkLabel(
            info_section,
            text="ℹ️  Database Info",
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        info_ttl.pack(padx=15, pady=(14, 6), anchor="w")

        # Compute DB size
        try:
            db_size_bytes = os.path.getsize(DB_PATH)
            db_size_str = f"{db_size_bytes / 1024:.1f} KB" if db_size_bytes < 1_048_576 else f"{db_size_bytes / 1_048_576:.2f} MB"
        except FileNotFoundError:
            db_size_str = "Not found"

        info_text = f"📂 Path:  {DB_PATH}\n💾 Size:   {db_size_str}"
        info_val = customtkinter.CTkLabel(
            info_section,
            text=info_text,
            font=customtkinter.CTkFont(size=11, family="Consolas"),
            text_color=PALETTE["SUBTEXT"],
            justify="left"
        )
        info_val.pack(padx=15, pady=(0, 14), anchor="w")

    def _export_csv(self):
        filepath = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"finance_export_{datetime.date.today()}.csv",
            title="Export All Transactions to CSV"
        )
        if not filepath:
            return

        try:
            all_txns = self.finance_service.get_transactions()
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "date", "type", "category_name", "description", "amount"])
                writer.writeheader()
                for t in all_txns:
                    writer.writerow({
                        "id": t["id"],
                        "date": t["date"],
                        "type": t["type"],
                        "category_name": t.get("category_name", ""),
                        "description": t.get("description", ""),
                        "amount": t["amount"]
                    })
            messagebox.showinfo("Export Successful", f"✅ {len(all_txns)} transactions exported to:\n{filepath}", parent=self.winfo_toplevel())
        except Exception as e:
            messagebox.showerror("Export Failed", str(e), parent=self.winfo_toplevel())

    def _clear_all_data(self):
        # Step 1: Initial confirmation
        first = messagebox.askyesno(
            "⚠️ Clear All Data",
            "This will permanently delete:\n\n  • All Transactions\n  • All Budgets\n  • All Savings Goals\n\nCategories and settings will NOT be affected.\n\nAre you sure you want to continue?",
            parent=self.winfo_toplevel()
        )
        if not first:
            return

        # Step 2: Type-to-confirm dialog
        confirm_win = customtkinter.CTkToplevel(self.winfo_toplevel())
        confirm_win.title("⚠️ Final Confirmation")
        confirm_win.geometry("400x220")
        confirm_win.resizable(False, False)
        confirm_win.configure(fg_color=PALETTE["CARD"])
        confirm_win.transient(self.winfo_toplevel())
        confirm_win.grab_set()

        lbl = customtkinter.CTkLabel(
            confirm_win,
            text="Type  DELETE  below to confirm:",
            font=customtkinter.CTkFont(size=13, weight="bold"),
            text_color=PALETTE["DANGER"]
        )
        lbl.pack(padx=20, pady=(25, 10))

        confirm_entry = customtkinter.CTkEntry(confirm_win, placeholder_text="Type DELETE here", width=220)
        confirm_entry.pack(padx=20, pady=(0, 15))

        def do_clear():
            if confirm_entry.get().strip() != "DELETE":
                messagebox.showerror("Incorrect", "You must type DELETE exactly to confirm.", parent=confirm_win)
                return
            confirm_win.destroy()
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions;")
                cursor.execute("DELETE FROM budgets;")
                cursor.execute("DELETE FROM savings_goals;")
                conn.commit()
                messagebox.showinfo("Done", "✅ All data has been cleared successfully.", parent=self.winfo_toplevel())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear data:\n{e}", parent=self.winfo_toplevel())

        btn_row = customtkinter.CTkFrame(confirm_win, fg_color="transparent")
        btn_row.pack(padx=20, fill="x")

        cancel_btn = customtkinter.CTkButton(btn_row, text="Cancel", fg_color="transparent", border_width=1, text_color=PALETTE["TEXT"], command=confirm_win.destroy)
        cancel_btn.pack(side="left", expand=True, padx=(0, 5), fill="x")

        clear_btn = customtkinter.CTkButton(btn_row, text="🗑️ Clear All", fg_color=PALETTE["DANGER"], hover_color="#dc2626", command=do_clear)
        clear_btn.pack(side="right", expand=True, padx=(5, 0), fill="x")

    def refresh(self):
        pass
