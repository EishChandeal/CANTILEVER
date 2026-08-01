import datetime
from tkinter import messagebox
import customtkinter

from src.gui.pages.base_frame import BaseFrame
from src.config import PALETTE
from src.utils.helpers import format_currency, format_date

class NewGoalDialog(customtkinter.CTkToplevel):
    """Modal dialog for creating a new savings goal."""

    def __init__(self, parent, on_save=None):
        super().__init__(parent)

        self.title("New Savings Goal")
        self.geometry("400x350")
        self.resizable(False, False)
        self.on_save = on_save

        self.transient(parent)
        self.grab_set()

        self.configure(fg_color=PALETTE["CARD"])

        # Title
        hdr = customtkinter.CTkLabel(
            self,
            text="🎯 New Savings Goal",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        hdr.pack(padx=20, pady=(20, 15), anchor="w")

        # Goal Name Entry
        name_lbl = customtkinter.CTkLabel(self, text="Goal Name", font=customtkinter.CTkFont(size=12, weight="bold"), text_color=PALETTE["SUBTEXT"])
        name_lbl.pack(padx=20, anchor="w")
        self.name_entry = customtkinter.CTkEntry(self, placeholder_text="e.g. Emergency Fund, New Laptop")
        self.name_entry.pack(padx=20, pady=(2, 12), fill="x")

        # Target Amount Entry
        target_lbl = customtkinter.CTkLabel(self, text="Target Amount (₹)", font=customtkinter.CTkFont(size=12, weight="bold"), text_color=PALETTE["SUBTEXT"])
        target_lbl.pack(padx=20, anchor="w")
        self.target_entry = customtkinter.CTkEntry(self, placeholder_text="e.g. 50000")
        self.target_entry.pack(padx=20, pady=(2, 12), fill="x")

        # Deadline Entry
        dl_lbl = customtkinter.CTkLabel(self, text="Deadline Date (YYYY-MM-DD)", font=customtkinter.CTkFont(size=12, weight="bold"), text_color=PALETTE["SUBTEXT"])
        dl_lbl.pack(padx=20, anchor="w")
        self.dl_entry = customtkinter.CTkEntry(self, placeholder_text="YYYY-MM-DD")
        self.dl_entry.pack(padx=20, pady=(2, 20), fill="x")

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
            text="Create Goal",
            fg_color=PALETTE["ACCENT"],
            command=self._on_save
        )
        save_btn.pack(side="right", expand=True, padx=(5, 0), fill="x")

    def _on_save(self):
        name = self.name_entry.get().strip()
        target_str = self.target_entry.get().strip()
        deadline_str = self.dl_entry.get().strip()

        if not name:
            messagebox.showerror("Invalid Name", "Please enter a goal name.", parent=self)
            return

        try:
            target = float(target_str)
            if target <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Invalid Target", "Please enter a positive numeric target amount.", parent=self)
            return

        if deadline_str:
            try:
                datetime.datetime.strptime(deadline_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Invalid Date", "Deadline date must be in YYYY-MM-DD format.", parent=self)
                return

        if self.on_save:
            self.on_save(name, target, deadline_str if deadline_str else None)
        self.destroy()


class AddFundsDialog(customtkinter.CTkToplevel):
    """Modal dialog for depositing money into a savings goal."""

    def __init__(self, parent, goal_name: str, on_save=None):
        super().__init__(parent)

        self.title(f"Deposit to {goal_name}")
        self.geometry("360x220")
        self.resizable(False, False)
        self.on_save = on_save

        self.transient(parent)
        self.grab_set()

        self.configure(fg_color=PALETTE["CARD"])

        hdr = customtkinter.CTkLabel(
            self,
            text=f"💰 Deposit to '{goal_name}'",
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        hdr.pack(padx=20, pady=(20, 15), anchor="w")

        amt_lbl = customtkinter.CTkLabel(self, text="Amount to Add (₹)", font=customtkinter.CTkFont(size=12, weight="bold"), text_color=PALETTE["SUBTEXT"])
        amt_lbl.pack(padx=20, anchor="w")

        self.amt_entry = customtkinter.CTkEntry(self, placeholder_text="0.00")
        self.amt_entry.pack(padx=20, pady=(2, 20), fill="x")

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
            text="Deposit",
            fg_color=PALETTE["SUCCESS"],
            command=self._on_save
        )
        save_btn.pack(side="right", expand=True, padx=(5, 0), fill="x")

    def _on_save(self):
        try:
            amount = float(self.amt_entry.get().strip())
            if amount <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Invalid Amount", "Please enter a positive numeric contribution.", parent=self)
            return

        if self.on_save:
            self.on_save(amount)
        self.destroy()


class SavingsFrame(BaseFrame):
    """Savings Goals management page with goal cards and progress tracking."""

    def __init__(self, parent, db_manager, services: dict):
        super().__init__(parent, db_manager, services)
        self.savings_service = services["savings"]
        self.settings_service = services["settings"]

        self.grid_columnconfigure(0, weight=1)

        # Header Toolbar
        self.toolbar = customtkinter.CTkFrame(self, fg_color=PALETTE["CARD"], corner_radius=10)
        self.toolbar.pack(padx=20, pady=(15, 15), fill="x")

        title_lbl = customtkinter.CTkLabel(
            self.toolbar,
            text="💰 Savings Goals",
            font=customtkinter.CTkFont(size=16, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        title_lbl.pack(side="left", padx=15, pady=12)

        add_btn = customtkinter.CTkButton(
            self.toolbar,
            text="＋ New Goal",
            fg_color=PALETTE["ACCENT"],
            command=self._open_new_goal_dialog
        )
        add_btn.pack(side="right", padx=15, pady=12)

        # Cards Container
        self.cards_container = customtkinter.CTkFrame(self, fg_color="transparent")
        self.cards_container.pack(padx=20, pady=(0, 20), fill="both", expand=True)

    def refresh(self):
        """Fetches all savings goals and renders 2-column cards grid."""
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        goals = self.savings_service.get_all_goals()
        symbol = self.settings_service.get_currency_symbol()

        if not goals:
            empty_box = customtkinter.CTkFrame(self.cards_container, fg_color=PALETTE["CARD"], corner_radius=10)
            empty_box.pack(padx=20, pady=40, fill="x")

            empty_lbl = customtkinter.CTkLabel(
                empty_box,
                text="No savings goals created yet.\nClick '＋ New Goal' above to set your financial targets!",
                font=customtkinter.CTkFont(size=14),
                text_color=PALETTE["SUBTEXT"]
            )
            empty_lbl.pack(pady=30)
            return

        self.cards_container.grid_columnconfigure((0, 1), weight=1, uniform="scard")

        for idx, g in enumerate(goals):
            row = idx // 2
            col = idx % 2

            card = customtkinter.CTkFrame(self.cards_container, fg_color=PALETTE["CARD"], corner_radius=10)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            # Header Row inside Card
            hdr_frame = customtkinter.CTkFrame(card, fg_color="transparent")
            hdr_frame.pack(padx=15, pady=(12, 4), fill="x")

            goal_name_lbl = customtkinter.CTkLabel(
                hdr_frame,
                text=f"🎯 {g['name']}",
                font=customtkinter.CTkFont(size=14, weight="bold"),
                text_color=PALETTE["TEXT"]
            )
            goal_name_lbl.pack(side="left", anchor="w")

            # Status Badge Pill
            is_completed = g["status"] == "completed"
            badge_bg = PALETTE["SUCCESS"] if is_completed else PALETTE["ACCENT"]
            badge_text = "Completed ✓" if is_completed else "Active"

            badge_lbl = customtkinter.CTkLabel(
                hdr_frame,
                text=f" {badge_text} ",
                font=customtkinter.CTkFont(size=11, weight="bold"),
                fg_color=badge_bg,
                text_color="#ffffff",
                corner_radius=6
            )
            badge_lbl.pack(side="right", anchor="e")

            # Progress Bar
            ratio = min(g["current_amount"] / g["target_amount"], 1.0) if g["target_amount"] > 0 else 0.0
            pbar = customtkinter.CTkProgressBar(
                card,
                height=10,
                progress_color=PALETTE["SUCCESS"] if is_completed else PALETTE["ACCENT"]
            )
            pbar.set(ratio)
            pbar.pack(padx=15, pady=6, fill="x")

            # Amount Details
            amt_info = f"{format_currency(g['current_amount'], symbol)} / {format_currency(g['target_amount'], symbol)} ({g['percent_complete']}%)"
            amt_lbl = customtkinter.CTkLabel(
                card,
                text=amt_info,
                font=customtkinter.CTkFont(size=12, weight="bold"),
                text_color=PALETTE["TEXT"]
            )
            amt_lbl.pack(padx=15, pady=(0, 2), anchor="w")

            # Deadline Details
            if g.get("deadline"):
                dl_text = f"Due: {format_date(g['deadline'])}"
                dl_lbl = customtkinter.CTkLabel(
                    card,
                    text=dl_text,
                    font=customtkinter.CTkFont(size=11),
                    text_color=PALETTE["SUBTEXT"]
                )
                dl_lbl.pack(padx=15, pady=(0, 10), anchor="w")

            # Action Buttons Row
            btn_frame = customtkinter.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(padx=15, pady=(0, 12), fill="x")

            if not is_completed:
                add_funds_btn = customtkinter.CTkButton(
                    btn_frame,
                    text="＋ Add Funds",
                    height=28,
                    fg_color=PALETTE["SUCCESS"],
                    hover_color="#16a34a",
                    command=lambda g_id=g["id"], g_name=g["name"]: self._open_deposit_dialog(g_id, g_name)
                )
                add_funds_btn.pack(side="left", padx=(0, 5))

                comp_btn = customtkinter.CTkButton(
                    btn_frame,
                    text="✓ Complete",
                    width=80,
                    height=28,
                    fg_color="transparent",
                    border_width=1,
                    text_color=PALETTE["TEXT"],
                    command=lambda g_id=g["id"]: self._complete_goal(g_id)
                )
                comp_btn.pack(side="left", padx=5)

            del_btn = customtkinter.CTkButton(
                btn_frame,
                text="🗑️ Delete",
                width=70,
                height=28,
                fg_color="transparent",
                border_width=1,
                text_color=PALETTE["DANGER"],
                command=lambda g_id=g["id"]: self._delete_goal(g_id)
            )
            del_btn.pack(side="right", padx=(5, 0))

    def _open_new_goal_dialog(self):
        def on_save(name, target, deadline):
            self.savings_service.create_goal(name, target, deadline)
            self.refresh()

        NewGoalDialog(parent=self.winfo_toplevel(), on_save=on_save)

    def _open_deposit_dialog(self, goal_id: int, goal_name: str):
        def on_save(amount):
            self.savings_service.add_funds(goal_id, amount)
            self.refresh()

        AddFundsDialog(parent=self.winfo_toplevel(), goal_name=goal_name, on_save=on_save)

    def _complete_goal(self, goal_id: int):
        self.savings_service.complete_goal(goal_id)
        self.refresh()

    def _delete_goal(self, goal_id: int):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this savings goal?", parent=self.winfo_toplevel())
        if confirm:
            self.savings_service.delete_goal(goal_id)
            self.refresh()
