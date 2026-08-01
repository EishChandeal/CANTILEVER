import datetime
import customtkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.gui.pages.base_frame import BaseFrame
from src.config import PALETTE
from src.utils.helpers import format_currency, format_date

class DashboardFrame(BaseFrame):
    """Dashboard page showing summary cards, horizontal expense chart, budget health, and recent activity."""

    def __init__(self, parent, db_manager, services: dict):
        super().__init__(parent, db_manager, services)
        self.finance_service = services["finance"]
        self.budget_service = services["budget"]
        self.settings_service = services["settings"]

        self.grid_columnconfigure(0, weight=1)

        # 1. Summary Cards Frame
        self.cards_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(padx=20, pady=(15, 10), fill="x")
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")

        # Card 1: Income
        self.card_inc = customtkinter.CTkFrame(self.cards_frame, fg_color=PALETTE["CARD"], corner_radius=10)
        self.card_inc.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        inc_title = customtkinter.CTkLabel(self.card_inc, text="💚 Total Income", font=customtkinter.CTkFont(size=13, weight="bold"), text_color=PALETTE["SUBTEXT"])
        inc_title.pack(padx=15, pady=(12, 2), anchor="w")
        self.inc_amt_label = customtkinter.CTkLabel(self.card_inc, text="₹ 0.00", font=customtkinter.CTkFont(size=22, weight="bold"), text_color=PALETTE["SUCCESS"])
        self.inc_amt_label.pack(padx=15, pady=(0, 12), anchor="w")

        # Card 2: Expenses
        self.card_exp = customtkinter.CTkFrame(self.cards_frame, fg_color=PALETTE["CARD"], corner_radius=10)
        self.card_exp.grid(row=0, column=1, padx=4, sticky="ew")
        exp_title = customtkinter.CTkLabel(self.card_exp, text="🔴 Total Expenses", font=customtkinter.CTkFont(size=13, weight="bold"), text_color=PALETTE["SUBTEXT"])
        exp_title.pack(padx=15, pady=(12, 2), anchor="w")
        self.exp_amt_label = customtkinter.CTkLabel(self.card_exp, text="₹ 0.00", font=customtkinter.CTkFont(size=22, weight="bold"), text_color=PALETTE["DANGER"])
        self.exp_amt_label.pack(padx=15, pady=(0, 12), anchor="w")

        # Card 3: Net Savings
        self.card_net = customtkinter.CTkFrame(self.cards_frame, fg_color=PALETTE["CARD"], corner_radius=10)
        self.card_net.grid(row=0, column=2, padx=(8, 0), sticky="ew")
        net_title = customtkinter.CTkLabel(self.card_net, text="🔵 Net Savings", font=customtkinter.CTkFont(size=13, weight="bold"), text_color=PALETTE["SUBTEXT"])
        net_title.pack(padx=15, pady=(12, 2), anchor="w")
        self.net_amt_label = customtkinter.CTkLabel(self.card_net, text="₹ 0.00", font=customtkinter.CTkFont(size=22, weight="bold"), text_color=PALETTE["ACCENT"])
        self.net_amt_label.pack(padx=15, pady=(0, 12), anchor="w")

        # 2. Middle Row: Expense Chart Container
        self.chart_container = customtkinter.CTkFrame(self, fg_color=PALETTE["CARD"], corner_radius=10)
        self.chart_container.pack(padx=20, pady=10, fill="x")

        chart_hdr = customtkinter.CTkLabel(
            self.chart_container,
            text="📊 Expense Breakdown (This Month)",
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        chart_hdr.pack(padx=15, pady=(12, 5), anchor="w")

        self.chart_body = customtkinter.CTkFrame(self.chart_container, fg_color="transparent")
        self.chart_body.pack(padx=15, pady=(0, 12), fill="both", expand=True)

        # 3. Bottom Row Split: Budget Health (Left) & Recent Activity (Right)
        self.bottom_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(padx=20, pady=(0, 20), fill="x")
        self.bottom_frame.grid_columnconfigure((0, 1), weight=1, uniform="bottom")

        # 3a. Budget Health Section
        self.budget_box = customtkinter.CTkFrame(self.bottom_frame, fg_color=PALETTE["CARD"], corner_radius=10)
        self.budget_box.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        budget_hdr = customtkinter.CTkLabel(
            self.budget_box,
            text="🎯 Budget Health",
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        budget_hdr.pack(padx=15, pady=(12, 8), anchor="w")

        self.budget_list_frame = customtkinter.CTkFrame(self.budget_box, fg_color="transparent")
        self.budget_list_frame.pack(padx=15, pady=(0, 12), fill="both", expand=True)

        # 3b. Recent Activity Section
        self.recent_box = customtkinter.CTkFrame(self.bottom_frame, fg_color=PALETTE["CARD"], corner_radius=10)
        self.recent_box.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        recent_hdr = customtkinter.CTkLabel(
            self.recent_box,
            text="📋 Recent Transactions",
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        recent_hdr.pack(padx=15, pady=(12, 8), anchor="w")

        self.recent_list_frame = customtkinter.CTkFrame(self.recent_box, fg_color="transparent")
        self.recent_list_frame.pack(padx=15, pady=(0, 12), fill="both", expand=True)

        # Animation tracking variables
        self._anim_job_inc = None
        self._anim_job_exp = None
        self._anim_job_net = None

    def refresh(self):
        """Fetches data for current month and updates all dashboard widgets."""
        today = datetime.date.today()
        month = today.month
        year = today.year
        symbol = self.settings_service.get_currency_symbol()

        # 1. Update Summary Cards with Count-Up Animation
        summary = self.finance_service.get_monthly_summary(month, year)
        self._animate_card_value(self.inc_amt_label, summary["income"], symbol)
        self._animate_card_value(self.exp_amt_label, summary["expense"], symbol)
        
        net_val = summary["net_savings"]
        self.net_amt_label.configure(text_color=PALETTE["SUCCESS"] if net_val >= 0 else PALETTE["DANGER"])
        self._animate_card_value(self.net_amt_label, net_val, symbol)

        # 2. Render Expense Breakdown Chart
        self._render_expense_chart(month, year, symbol)

        # 3. Render Budget Health
        self._render_budget_health(month, year, symbol)

        # 4. Render Recent Activity
        self._render_recent_activity(symbol)

    def _animate_card_value(self, label_widget, target_val: float, symbol: str, steps: int = 15, current_step: int = 0):
        """Smooth count-up animation for summary cards."""
        if current_step >= steps:
            label_widget.configure(text=format_currency(target_val, symbol))
            return

        intermediate_val = target_val * (current_step / steps)
        label_widget.configure(text=format_currency(intermediate_val, symbol))

        self.after(20, lambda: self._animate_card_value(label_widget, target_val, symbol, steps, current_step + 1))

    def _render_expense_chart(self, month: int, year: int, symbol: str):
        """Embeds horizontal bar chart for top expense categories using Matplotlib."""
        for widget in self.chart_body.winfo_children():
            widget.destroy()

        breakdown = self.finance_service.get_category_breakdown(month, year, type_="expense")

        if not breakdown:
            no_data_label = customtkinter.CTkLabel(
                self.chart_body,
                text="No expenses recorded for this month.",
                font=customtkinter.CTkFont(size=13),
                text_color=PALETTE["SUBTEXT"]
            )
            no_data_label.pack(pady=30)
            return

        # Prepare data for horizontal bar chart (Top 5 categories)
        top_cats = breakdown[:5]
        cat_names = [c["category_name"] for c in reversed(top_cats)]
        amounts = [c["total"] for c in reversed(top_cats)]
        bar_colors = [c.get("color", PALETTE["ACCENT"]) for c in reversed(top_cats)]

        # Matplotlib Figure
        fig = Figure(figsize=(7, 2.2), dpi=100)
        fig.patch.set_facecolor(PALETTE["CARD"])

        ax = fig.add_subplot(111)
        ax.set_facecolor(PALETTE["CARD"])

        bars = ax.barh(cat_names, amounts, color=bar_colors, height=0.55)

        # Remove borders & ticks formatting
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        ax.xaxis.set_visible(False)
        ax.tick_params(axis='y', colors=PALETTE["TEXT"], labelsize=10)

        # Add text labels at bar tips
        max_val = max(amounts) if amounts else 1
        for bar, amt in zip(bars, amounts):
            width = bar.get_width()
            ax.text(
                width + (max_val * 0.02),
                bar.get_y() + bar.get_height() / 2,
                f"{symbol} {amt:,.2f}",
                va='center',
                ha='left',
                color=PALETTE["TEXT"],
                fontsize=9,
                fontweight='bold'
            )

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_body)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _render_budget_health(self, month: int, year: int, symbol: str):
        """Renders mini progress bars for category budgets."""
        for widget in self.budget_list_frame.winfo_children():
            widget.destroy()

        budgets = self.budget_service.get_budget_vs_actual(month, year)

        if not budgets:
            no_b_label = customtkinter.CTkLabel(
                self.budget_list_frame,
                text="No budgets configured for this month.",
                font=customtkinter.CTkFont(size=12),
                text_color=PALETTE["SUBTEXT"]
            )
            no_b_label.pack(pady=20)
            return

        for b in budgets[:4]:  # Show top 4
            row = customtkinter.CTkFrame(self.budget_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)

            # Left: Category Name + Dot
            title_text = f"● {b['category_name']}"
            if b["percent_used"] >= 80.0:
                title_text += " ⚠️"

            cat_lbl = customtkinter.CTkLabel(
                row,
                text=title_text,
                font=customtkinter.CTkFont(size=12, weight="bold"),
                text_color=b["color"]
            )
            cat_lbl.pack(side="left", anchor="w")

            # Right: Spent / Budget label
            amt_lbl = customtkinter.CTkLabel(
                row,
                text=f"{format_currency(b['spent'], symbol)} / {format_currency(b['budget'], symbol)} ({b['percent_used']}%)",
                font=customtkinter.CTkFont(size=11),
                text_color=PALETTE["SUBTEXT"]
            )
            amt_lbl.pack(side="right", anchor="e")

            # Progress Bar below
            ratio = min(b["spent"] / b["budget"], 1.0) if b["budget"] > 0 else 0.0

            if ratio >= 0.90:
                p_color = PALETTE["DANGER"]
            elif ratio >= 0.70:
                p_color = PALETTE["WARNING"]
            else:
                p_color = PALETTE["SUCCESS"]

            pbar = customtkinter.CTkProgressBar(
                self.budget_list_frame,
                height=8,
                progress_color=p_color
            )
            pbar.set(ratio)
            pbar.pack(fill="x", pady=(0, 6))

    def _render_recent_activity(self, symbol: str):
        """Renders list of recent transactions."""
        for widget in self.recent_list_frame.winfo_children():
            widget.destroy()

        recent = self.finance_service.get_recent_transactions(limit=6)

        if not recent:
            no_r_label = customtkinter.CTkLabel(
                self.recent_list_frame,
                text="No recent transactions.",
                font=customtkinter.CTkFont(size=12),
                text_color=PALETTE["SUBTEXT"]
            )
            no_r_label.pack(pady=20)
            return

        for t in recent:
            row = customtkinter.CTkFrame(self.recent_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)

            # Left side: Date + Category + Description
            left_sub = customtkinter.CTkFrame(row, fg_color="transparent")
            left_sub.pack(side="left", anchor="w")

            desc = t.get("description") or t.get("category_name") or "Transaction"
            cat_name = t.get("category_name") or ""

            desc_lbl = customtkinter.CTkLabel(
                left_sub,
                text=f"● {desc} ({cat_name})",
                font=customtkinter.CTkFont(size=12, weight="bold"),
                text_color=t.get("category_color") or PALETTE["TEXT"],
                anchor="w"
            )
            desc_lbl.pack(anchor="w")

            date_lbl = customtkinter.CTkLabel(
                left_sub,
                text=format_date(t["date"]),
                font=customtkinter.CTkFont(size=10),
                text_color=PALETTE["SUBTEXT"],
                anchor="w"
            )
            date_lbl.pack(anchor="w")

            # Right side: Amount (+ or -)
            is_inc = t["type"] == "income"
            amt_prefix = "+" if is_inc else "-"
            color = PALETTE["SUCCESS"] if is_inc else PALETTE["DANGER"]

            amt_lbl = customtkinter.CTkLabel(
                row,
                text=f"{amt_prefix}{format_currency(t['amount'], symbol)}",
                font=customtkinter.CTkFont(size=12, weight="bold"),
                text_color=color
            )
            amt_lbl.pack(side="right", anchor="e")
