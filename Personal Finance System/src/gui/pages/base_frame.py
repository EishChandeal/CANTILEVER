import customtkinter
from src.config import PALETTE

class BaseFrame(customtkinter.CTkScrollableFrame):
    """Base class for all page frames in the Personal Finance System."""

    def __init__(self, parent, db_manager, services: dict):
        super().__init__(
            parent,
            corner_radius=0,
            fg_color=PALETTE["BG"]
        )
        self.db_manager = db_manager
        self.services = services

    def refresh(self):
        """Called automatically when the frame is brought into view."""
        pass
