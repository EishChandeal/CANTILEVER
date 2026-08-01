import sys
from pathlib import Path

# Add project root to sys.path only in dev mode.
# When frozen by PyInstaller (sys.frozen=True) the bundled PYZ archive already
# contains all src.* modules — inserting the source path would cause the exe to
# load .py files from disk (the original project folder) instead of the bundle,
# which breaks the sys.frozen path resolution in config.py.
if not getattr(sys, 'frozen', False):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import customtkinter
from src.config import APPEARANCE_MODE, COLOR_THEME
from src.database.db_manager import DatabaseManager
from src.gui.app import App

def main():
    # Configure CustomTkinter Theme & Appearance Mode
    customtkinter.set_appearance_mode(APPEARANCE_MODE)
    customtkinter.set_default_color_theme(COLOR_THEME)

    # Initialize Database Manager
    db_manager = DatabaseManager()

    # Launch GUI Application
    app = App(db_manager=db_manager)

    # Ensure clean database closure on exit
    def on_closing():
        db_manager.close()
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()
