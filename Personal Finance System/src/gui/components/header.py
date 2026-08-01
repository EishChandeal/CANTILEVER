import customtkinter
from datetime import datetime
from src.config import PALETTE

class Header(customtkinter.CTkFrame):
    """Header bar with page title and real-time ticking clock."""

    def __init__(self, parent, initial_title: str = "Dashboard"):
        super().__init__(
            parent,
            height=65,
            corner_radius=0,
            fg_color=PALETTE["CARD"]
        )
        self.pack_propagate(False)

        # Title Label (Left)
        self.title_label = customtkinter.CTkLabel(
            self,
            text=initial_title,
            font=customtkinter.CTkFont(size=20, weight="bold"),
            text_color=PALETTE["TEXT"]
        )
        self.title_label.pack(side="left", padx=25)

        # Real-time Clock Label (Right)
        self.clock_label = customtkinter.CTkLabel(
            self,
            text="",
            font=customtkinter.CTkFont(size=13),
            text_color=PALETTE["SUBTEXT"]
        )
        self.clock_label.pack(side="right", padx=25)

        # Start live clock tick loop
        self._update_clock()

    def set_title(self, title: str):
        """Updates the page title displayed in the header."""
        self.title_label.configure(text=title)

    def _update_clock(self):
        """Updates the clock text every second."""
        now = datetime.now().strftime("%a, %d %b %Y | %I:%M:%S %p")
        self.clock_label.configure(text=now)
        self.after(1000, self._update_clock)
