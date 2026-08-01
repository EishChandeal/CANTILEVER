import os
import sys
from pathlib import Path

# Base Directory Resolution (Dev vs Packaged Exe)
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

# Data & Database Paths
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "finance.db"

# Application Settings
APP_NAME = "Personal Finance System"
CURRENCY_SYMBOL = "₹"
CURRENCY_CODE = "INR"
APPEARANCE_MODE = "dark"
COLOR_THEME = "blue"

# UI Palette Configuration
PALETTE = {
    "BG": "#0f172a",
    "SIDEBAR": "#1e293b",
    "CARD": "#1e293b",
    "ACCENT": "#3b82f6",
    "SUCCESS": "#22c55e",
    "DANGER": "#ef4444",
    "WARNING": "#f59e0b",
    "TEXT": "#f1f5f9",
    "SUBTEXT": "#94a3b8"
}
