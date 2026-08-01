import customtkinter
from src.config import PALETTE

class Sidebar(customtkinter.CTkFrame):
    """Sidebar navigation menu component."""

    NAV_ITEMS = [
        ("dashboard", "🏠  Dashboard"),
        ("transactions", "📋  Transactions"),
        ("budget", "🎯  Budget"),
        ("savings", "💰  Savings"),
        ("reports", "📊  Reports"),
        ("settings", "⚙️  Settings"),
    ]

    def __init__(self, parent, on_navigate_callback):
        super().__init__(
            parent,
            width=220,
            corner_radius=0,
            fg_color=PALETTE["SIDEBAR"]
        )
        self.on_navigate_callback = on_navigate_callback
        self.buttons = {}
        self.active_page = "dashboard"

        # Prevent grid from resizing sidebar
        self.grid_propagate(False)
        self.pack_propagate(False)

        # Header Title / Logo
        self.logo_label = customtkinter.CTkLabel(
            self,
            text="💰 Finance",
            font=customtkinter.CTkFont(size=22, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        self.logo_label.pack(padx=20, pady=(25, 30), anchor="w")

        # Navigation Buttons
        for page_key, label_text in self.NAV_ITEMS:
            btn = customtkinter.CTkButton(
                self,
                text=label_text,
                font=customtkinter.CTkFont(size=14, weight="bold"),
                height=42,
                corner_radius=8,
                anchor="w",
                fg_color="transparent",
                text_color=PALETTE["TEXT"],
                hover_color="#334155",
                command=lambda key=page_key: self._on_button_click(key)
            )
            btn.pack(padx=15, pady=4, fill="x")
            self.buttons[page_key] = btn

        # Version label at bottom
        self.version_label = customtkinter.CTkLabel(
            self,
            text="v1.0.0",
            font=customtkinter.CTkFont(size=11),
            text_color=PALETTE["SUBTEXT"]
        )
        self.version_label.pack(side="bottom", pady=20)

        # Highlight default page
        self.set_active(self.active_page)

    def _on_button_click(self, page_key: str):
        self.set_active(page_key)
        if self.on_navigate_callback:
            self.on_navigate_callback(page_key)

    def set_active(self, page_key: str):
        self.active_page = page_key
        for key, btn in self.buttons.items():
            if key == page_key:
                btn.configure(
                    fg_color=PALETTE["ACCENT"],
                    text_color="#ffffff"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=PALETTE["TEXT"]
                )
