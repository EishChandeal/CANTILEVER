import customtkinter
from src.gui.pages.base_frame import BaseFrame
from src.config import PALETTE

class DashboardFrame(BaseFrame):
    def __init__(self, parent, db_manager, services: dict):
        super().__init__(parent, db_manager, services)
        
        self.label = customtkinter.CTkLabel(
            self,
            text="🏠 Dashboard Page — Coming Soon",
            font=customtkinter.CTkFont(size=18, weight="bold"),
            text_color=PALETTE["SUBTEXT"]
        )
        self.label.pack(expand=True, pady=100)

    def refresh(self):
        pass
