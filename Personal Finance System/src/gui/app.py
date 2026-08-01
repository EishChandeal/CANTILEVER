import customtkinter
from src.config import APP_NAME

class App(customtkinter.CTk):
    """Main application shell window using CustomTkinter."""

    def __init__(self, db_manager=None):
        super().__init__()

        self.db_manager = db_manager
        self.title(APP_NAME)
        self.geometry("1150x700")
        self.minsize(1150, 700)
