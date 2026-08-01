import sqlite3
from pathlib import Path
from src.config import DATA_DIR, DB_PATH

class DatabaseManager:
    """Manages SQLite database connections and storage directory setup."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        
        # Ensure data folder exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Establish connection with multithreading flag enabled for GUI responsiveness
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def get_connection(self) -> sqlite3.Connection:
        """Returns the active SQLite connection."""
        return self.conn

    def close(self):
        """Closes the SQLite database connection if open."""
        if self.conn:
            self.conn.close()
            self.conn = None
