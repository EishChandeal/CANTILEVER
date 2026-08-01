import calendar
import datetime
import csv
from tkinter import filedialog, messagebox
import customtkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from src.gui.pages.base_frame import BaseFrame
from src.config import PALETTE
from src.utils.helpers import format_currency

class ReportsFrame(BaseFrame):
    """Reports & Visualizations page with trend, breakdown, and comparison charts."""

    MONTHS = [("Jan", 1), ("Feb", 2), ("Mar", 3), ("Apr", 4),
              ("May", 5), ("Jun", 6), ("Jul", 7), ("Aug", 8),
              ("Sep", 9), ("Oct", 10), ("Nov", 11), ("Dec", 12)]

    def __init__(self, parent, db_manager, services: dict):
        super().__init__(parent, db_manager, services)
        self.finance_service = services["finance"]
        self.settings_service = services["settings"]

        self.current_year = datetime.date.today().year
        self.current_month = datetime.date.today().month
        self._current_figure = None

        # Outer layout: side-by-side (no scrollable needed at top level)
        self.outer = customtkinter.CTkFrame(self, fg_color="transparent")
        self.outer.pack(fill="both", expand=True, padx=0, pady=0)
        self.outer.grid_columnconfigure(0, weight=0, minsize=250)
        self.outer.grid_columnconfigure(1, weight=1)
        self.outer.grid_rowconfigure(0, weight=1)

        # ── Left Control Panel ──────────────────────────────────────────────
        self.control_panel = customtkinter.CTkFrame(
            self.outer,
            width=250,
            fg_color=PALETTE["CARD"],
            corner_radius=0
        )
        self.control_panel.grid(row=0, column=0, sticky="nsew")
        self.control_panel.pack_propagate(False)
        self.control_panel.grid_propagate(False)

        # Heading
        heading = customtkinter.CTkLabel(
            self.control_panel,
            text="📊 Reports",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        heading.pack(padx=20, pady=(22, 15), anchor="w")

        # Chart Type Selector
        type_lbl = customtkinter.CTkLabel(
            self.control_panel,
            text="Chart Type",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            text_color=PALETTE["SUBTEXT"]
        )
        type_lbl.pack(padx=20, anchor="w")

        self.chart_type_seg = customtkinter.CTkSegmentedButton(
            self.control_panel,
            values=["Trend", "Breakdown", "Comparison"],
            command=self._on_chart_type_change,
            selected_color=PALETTE["ACCENT"],
            font=customtkinter.CTkFont(size=12)
        )
        self.chart_type_seg.set("Trend")
        self.chart_type_seg.pack(padx=20, pady=(4, 15), fill="x")

        # ── Dynamic filter sections (shown/hidden based on chart type) ──────

        # --- TREND filters ---
        self.trend_frame = customtkinter.CTkFrame(self.control_panel, fg_color="transparent")
        self.trend_frame.pack(padx=20, fill="x")

        trend_lbl = customtkinter.CTkLabel(
            self.trend_frame,
            text="Last N months",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            text_color=PALETTE["SUBTEXT"]
        )
        trend_lbl.pack(anchor="w")

        self.trend_n_label = customtkinter.CTkLabel(
            self.trend_frame,
            text="6 months",
            font=customtkinter.CTkFont(size=11),
            text_color=PALETTE["TEXT"]
        )
        self.trend_n_label.pack(anchor="w", pady=(2, 0))

        self.trend_slider = customtkinter.CTkSlider(
            self.trend_frame,
            from_=3, to=12, number_of_steps=9,
            command=self._on_slider_change
        )
        self.trend_slider.set(6)
        self.trend_slider.pack(fill="x", pady=(2, 0))

        # --- BREAKDOWN filters ---
        self.breakdown_frame = customtkinter.CTkFrame(self.control_panel, fg_color="transparent")

        bd_m_lbl = customtkinter.CTkLabel(
            self.breakdown_frame,
            text="Month",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            text_color=PALETTE["SUBTEXT"]
        )
        bd_m_lbl.pack(anchor="w")

        month_labels = [m[0] for m in self.MONTHS]
        self.bd_month_opt = customtkinter.CTkOptionMenu(
            self.breakdown_frame,
            values=month_labels,
            width=200
        )
        self.bd_month_opt.set(self.MONTHS[self.current_month - 1][0])
        self.bd_month_opt.pack(fill="x", pady=(2, 10))

        bd_y_lbl = customtkinter.CTkLabel(
            self.breakdown_frame,
            text="Year",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            text_color=PALETTE["SUBTEXT"]
        )
        bd_y_lbl.pack(anchor="w")

        year_opts = [str(y) for y in range(self.current_year - 3, self.current_year + 2)]
        self.bd_year_opt = customtkinter.CTkOptionMenu(
            self.breakdown_frame,
            values=year_opts,
            width=200
        )
        self.bd_year_opt.set(str(self.current_year))
        self.bd_year_opt.pack(fill="x", pady=(2, 10))

        bd_type_lbl = customtkinter.CTkLabel(
            self.breakdown_frame,
            text="Transaction Type",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            text_color=PALETTE["SUBTEXT"]
        )
        bd_type_lbl.pack(anchor="w")

        self.bd_type_seg = customtkinter.CTkSegmentedButton(
            self.breakdown_frame,
            values=["Expense", "Income"],
            selected_color=PALETTE["ACCENT"]
        )
        self.bd_type_seg.set("Expense")
        self.bd_type_seg.pack(fill="x", pady=(2, 0))

        # --- COMPARISON filters ---
        self.comparison_frame = customtkinter.CTkFrame(self.control_panel, fg_color="transparent")

        comp_y_lbl = customtkinter.CTkLabel(
            self.comparison_frame,
            text="Year",
            font=customtkinter.CTkFont(size=12, weight="bold"),
            text_color=PALETTE["SUBTEXT"]
        )
        comp_y_lbl.pack(anchor="w")

        self.comp_year_opt = customtkinter.CTkOptionMenu(
            self.comparison_frame,
            values=year_opts,
            width=200
        )
        self.comp_year_opt.set(str(self.current_year))
        self.comp_year_opt.pack(fill="x", pady=(2, 0))

        # Refresh Button
        self.refresh_btn = customtkinter.CTkButton(
            self.control_panel,
            text="🔄  Refresh Chart",
            fg_color=PALETTE["ACCENT"],
            command=self._draw_chart
        )
        self.refresh_btn.pack(padx=20, pady=(20, 8), fill="x")

        # Divider
        div = customtkinter.CTkFrame(self.control_panel, height=1, fg_color=PALETTE["SIDEBAR"])
        div.pack(padx=20, pady=10, fill="x")

        # Export CSV Button
        export_csv_btn = customtkinter.CTkButton(
            self.control_panel,
            text="📥  Export CSV",
            fg_color="transparent",
            border_width=1,
            text_color=PALETTE["TEXT"],
            command=self._export_csv
        )
        export_csv_btn.pack(padx=20, pady=(0, 8), fill="x")

        # Save Chart PNG Button
        save_png_btn = customtkinter.CTkButton(
            self.control_panel,
            text="🖼  Save Chart as PNG",
            fg_color="transparent",
            border_width=1,
            text_color=PALETTE["TEXT"],
            command=self._save_chart_png
        )
        save_png_btn.pack(padx=20, pady=(0, 20), fill="x")

        # ── Right Chart Area ────────────────────────────────────────────────
        self.chart_area = customtkinter.CTkFrame(
            self.outer,
            fg_color=PALETTE["BG"],
            corner_radius=0
        )
        self.chart_area.grid(row=0, column=1, sticky="nsew", padx=(1, 0))

        self.canvas_frame = customtkinter.CTkFrame(self.chart_area, fg_color="transparent")
        self.canvas_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Show Trend by default on first load
        self._on_chart_type_change("Trend")

    # ── Filter visibility logic ──────────────────────────────────────────────

    def _on_chart_type_change(self, chart_type: str):
        """Shows/hides filter controls depending on selected chart type."""
        self.trend_frame.pack_forget()
        self.breakdown_frame.pack_forget()
        self.comparison_frame.pack_forget()

        if chart_type == "Trend":
            self.trend_frame.pack(padx=20, fill="x", pady=(0, 5))
        elif chart_type == "Breakdown":
            self.breakdown_frame.pack(padx=20, fill="x", pady=(0, 5))
        elif chart_type == "Comparison":
            self.comparison_frame.pack(padx=20, fill="x", pady=(0, 5))

    def _on_slider_change(self, val):
        n = int(val)
        self.trend_n_label.configure(text=f"{n} months")

    # ── Chart Rendering ──────────────────────────────────────────────────────

    def _clear_canvas(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        if self._current_figure:
            plt.close(self._current_figure)
            self._current_figure = None

    def _make_figure(self, figsize=(9, 5.5)):
        fig = Figure(figsize=figsize, dpi=100)
        fig.patch.set_facecolor(PALETTE["BG"])
        self._current_figure = fig
        return fig

    def _embed_figure(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _no_data_figure(self, message="No data available for the selected period."):
        fig = self._make_figure()
        ax = fig.add_subplot(111)
        ax.set_facecolor(PALETTE["CARD"])
        ax.text(0.5, 0.5, message, ha="center", va="center",
                color=PALETTE["SUBTEXT"], fontsize=14, transform=ax.transAxes)
        ax.axis("off")
        fig.tight_layout()
        self._embed_figure(fig)

    def _draw_chart(self):
        chart_type = self.chart_type_seg.get()
        self._clear_canvas()

        if chart_type == "Trend":
            self._draw_trend_chart()
        elif chart_type == "Breakdown":
            self._draw_breakdown_chart()
        elif chart_type == "Comparison":
            self._draw_comparison_chart()

    def _draw_trend_chart(self):
        months_n = int(self.trend_slider.get())
        symbol = self.settings_service.get_currency_symbol()
        trend_data = self.finance_service.get_trend_data(months=months_n)

        if not trend_data:
            self._no_data_figure("No transaction data available yet.\nAdd some transactions to see trends.")
            return

        labels = [d["month_label"] for d in trend_data]
        incomes = [d["income"] for d in trend_data]
        expenses = [d["expense"] for d in trend_data]
        savings = [d["savings"] for d in trend_data]

        fig = self._make_figure()
        ax = fig.add_subplot(111)
        ax.set_facecolor(PALETTE["CARD"])

        xs = range(len(labels))

        # Lines with filled areas
        ax.plot(xs, incomes, color=PALETTE["SUCCESS"], linewidth=2.5, label="Income", marker="o", markersize=5, zorder=3)
        ax.fill_between(xs, incomes, alpha=0.12, color=PALETTE["SUCCESS"])

        ax.plot(xs, expenses, color=PALETTE["DANGER"], linewidth=2.5, label="Expenses", marker="o", markersize=5, zorder=3)
        ax.fill_between(xs, expenses, alpha=0.12, color=PALETTE["DANGER"])

        ax.plot(xs, savings, color=PALETTE["ACCENT"], linewidth=2.5, label="Net Savings", marker="s", markersize=5, linestyle="--", zorder=3)
        ax.fill_between(xs, savings, alpha=0.10, color=PALETTE["ACCENT"])

        # Styling
        ax.set_xticks(list(xs))
        ax.set_xticklabels(labels, color=PALETTE["TEXT"], fontsize=10)
        ax.tick_params(axis="y", colors=PALETTE["SUBTEXT"], labelsize=9)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{symbol} {v:,.0f}"))

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(PALETTE["SIDEBAR"])
        ax.spines["bottom"].set_color(PALETTE["SIDEBAR"])

        ax.grid(axis="y", color=PALETTE["SIDEBAR"], linestyle="--", linewidth=0.8, alpha=0.7)
        ax.set_axisbelow(True)

        legend = ax.legend(facecolor=PALETTE["CARD"], edgecolor=PALETTE["SIDEBAR"],
                           labelcolor=PALETTE["TEXT"], fontsize=10)

        ax.set_title(f"Income vs Expenses vs Savings (Last {months_n} Months)",
                     color=PALETTE["TEXT"], fontsize=13, fontweight="bold", pad=12)

        fig.tight_layout(pad=1.5)
        self._embed_figure(fig)

    def _draw_breakdown_chart(self):
        sel_m = self.bd_month_opt.get()
        month_int = next((m[1] for m in self.MONTHS if m[0] == sel_m), self.current_month)
        year_int = int(self.bd_year_opt.get())
        tx_type = self.bd_type_seg.get().lower()
        symbol = self.settings_service.get_currency_symbol()

        breakdown = self.finance_service.get_category_breakdown(month_int, year_int, type_=tx_type)

        if not breakdown:
            self._no_data_figure(f"No {tx_type} data found for {sel_m} {year_int}.")
            return

        labels = [c["category_name"] for c in breakdown]
        amounts = [c["total"] for c in breakdown]
        colors = [c.get("color", PALETTE["ACCENT"]) for c in breakdown]
        total = sum(amounts)

        fig = self._make_figure(figsize=(9, 5.5))
        ax = fig.add_subplot(111)
        ax.set_facecolor(PALETTE["BG"])

        wedges, texts, autotexts = ax.pie(
            amounts,
            labels=None,
            colors=colors,
            startangle=140,
            pctdistance=0.78,
            wedgeprops={"width": 0.55, "edgecolor": PALETTE["BG"], "linewidth": 2},
            autopct=lambda pct: f"{pct:.1f}%"
        )
        for at in autotexts:
            at.set(color=PALETTE["TEXT"], fontsize=9, fontweight="bold")

        # Center Total Label
        ax.text(0, 0, f"Total\n{format_currency(total, symbol)}",
                ha="center", va="center",
                color=PALETTE["TEXT"], fontsize=11, fontweight="bold")

        # Legend with ₹ amounts
        legend_labels = [f"{lbl}  {format_currency(amt, symbol)}" for lbl, amt in zip(labels, amounts)]
        ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1.02, 0.5),
                  facecolor=PALETTE["CARD"], edgecolor=PALETTE["SIDEBAR"],
                  labelcolor=PALETTE["TEXT"], fontsize=9)

        ax.set_title(f"{tx_type.capitalize()} Breakdown — {sel_m} {year_int}",
                     color=PALETTE["TEXT"], fontsize=13, fontweight="bold")

        fig.tight_layout(pad=1.5)
        self._embed_figure(fig)

    def _draw_comparison_chart(self):
        year_int = int(self.comp_year_opt.get())
        symbol = self.settings_service.get_currency_symbol()

        month_labels = []
        incomes = []
        expenses = []

        for m_name, m_int in self.MONTHS:
            totals = self.finance_service.get_monthly_summary(m_int, year_int)
            month_labels.append(m_name)
            incomes.append(totals["income"])
            expenses.append(totals["expense"])

        if all(v == 0 for v in incomes) and all(v == 0 for v in expenses):
            self._no_data_figure(f"No transaction data found for {year_int}.")
            return

        fig = self._make_figure()
        ax = fig.add_subplot(111)
        ax.set_facecolor(PALETTE["CARD"])

        x = range(len(month_labels))
        bar_w = 0.38

        bars_inc = ax.bar(
            [i - bar_w / 2 for i in x], incomes,
            width=bar_w, color=PALETTE["SUCCESS"], label="Income",
            alpha=0.9, zorder=3
        )
        bars_exp = ax.bar(
            [i + bar_w / 2 for i in x], expenses,
            width=bar_w, color=PALETTE["DANGER"], label="Expenses",
            alpha=0.9, zorder=3
        )

        # Value labels on top of bars (skip zeros)
        for bar in bars_inc:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + (max(incomes + expenses) * 0.01),
                        f"{symbol}{h:,.0f}", ha="center", va="bottom",
                        color=PALETTE["SUCCESS"], fontsize=7.5, fontweight="bold")

        for bar in bars_exp:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + (max(incomes + expenses) * 0.01),
                        f"{symbol}{h:,.0f}", ha="center", va="bottom",
                        color=PALETTE["DANGER"], fontsize=7.5, fontweight="bold")

        # Styling
        ax.set_xticks(list(x))
        ax.set_xticklabels(month_labels, color=PALETTE["TEXT"], fontsize=10)
        ax.tick_params(axis="y", colors=PALETTE["SUBTEXT"], labelsize=9)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{symbol} {v:,.0f}"))

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(PALETTE["SIDEBAR"])
        ax.spines["bottom"].set_color(PALETTE["SIDEBAR"])

        ax.grid(axis="y", color=PALETTE["SIDEBAR"], linestyle="--", linewidth=0.8, alpha=0.7)
        ax.set_axisbelow(True)

        ax.legend(facecolor=PALETTE["CARD"], edgecolor=PALETTE["SIDEBAR"],
                  labelcolor=PALETTE["TEXT"], fontsize=10)

        ax.set_title(f"Income vs Expenses — Monthly Comparison {year_int}",
                     color=PALETTE["TEXT"], fontsize=13, fontweight="bold", pad=12)

        fig.tight_layout(pad=1.5)
        self._embed_figure(fig)

    # ── Export Handlers ──────────────────────────────────────────────────────

    def _export_csv(self):
        filepath = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="finance_export.csv",
            title="Export Transactions to CSV"
        )
        if not filepath:
            return

        try:
            all_txns = self.finance_service.get_transactions()
            symbol = self.settings_service.get_currency_symbol()

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

            messagebox.showinfo("Export Successful", f"Transactions exported to:\n{filepath}", parent=self.winfo_toplevel())
        except Exception as e:
            messagebox.showerror("Export Failed", str(e), parent=self.winfo_toplevel())

    def _save_chart_png(self):
        if not self._current_figure:
            messagebox.showwarning("No Chart", "Please render a chart first by clicking 'Refresh Chart'.", parent=self.winfo_toplevel())
            return

        filepath = filedialog.asksaveasfilename(
            parent=self.winfo_toplevel(),
            defaultextension=".png",
            filetypes=[("PNG Images", "*.png")],
            initialfile="finance_chart.png",
            title="Save Chart as PNG"
        )
        if not filepath:
            return

        try:
            self._current_figure.savefig(filepath, dpi=150, facecolor=self._current_figure.get_facecolor())
            messagebox.showinfo("Saved", f"Chart saved to:\n{filepath}", parent=self.winfo_toplevel())
        except Exception as e:
            messagebox.showerror("Save Failed", str(e), parent=self.winfo_toplevel())

    def refresh(self):
        """Called when the page is shown — renders the default trend chart."""
        self._draw_chart()
