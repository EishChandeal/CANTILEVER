import os
import sys
from pathlib import Path

# ─── Base Directory Resolution (Dev vs Packaged .exe) ────────────────────────
# When frozen by PyInstaller:
#   sys.frozen = True
#   sys._MEIPASS  = temporary bundle extraction dir (read-only assets)
#   sys.executable = path to the running .exe
#
# The database must live NEXT TO the .exe (writable), not inside _MEIPASS.
# ─────────────────────────────────────────────────────────────────────────────

if getattr(sys, 'frozen', False):
    # Running as a PyInstaller-packaged executable
    # Writable data (DB) goes in the same folder as the .exe
    BASE_DIR = Path(sys.executable).parent
    # Read-only bundled assets (icons, themes) come from _MEIPASS
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    # Running in normal Python / dev mode
    BASE_DIR = Path(__file__).resolve().parent.parent
    BUNDLE_DIR = BASE_DIR

# Data & Database Paths (always writable, next to .exe or project root)
DATA_DIR = BASE_DIR / "data"
DB_PATH  = DATA_DIR / "finance.db"

# Application Settings
APP_NAME       = "Personal Finance System"
CURRENCY_SYMBOL = "₹"
CURRENCY_CODE  = "INR"
APPEARANCE_MODE = "dark"
COLOR_THEME    = "blue"

# UI Palette Configuration
PALETTE = {
    "BG":      "#0f172a",
    "SIDEBAR": "#1e293b",
    "CARD":    "#1e293b",
    "ACCENT":  "#3b82f6",
    "SUCCESS": "#22c55e",
    "DANGER":  "#ef4444",
    "WARNING": "#f59e0b",
    "TEXT":    "#f1f5f9",
    "SUBTEXT": "#94a3b8"
}
