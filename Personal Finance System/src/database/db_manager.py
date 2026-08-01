import sqlite3
from pathlib import Path
from src.config import DATA_DIR, DB_PATH
from src.database.schema import initialize_db

class DatabaseManager:
    """Manages SQLite database connections and schema initialization."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open SQLite connection
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # Initialize schema and seed data
        initialize_db(self.conn)

    def get_connection(self) -> sqlite3.Connection:
        """Returns the active SQLite connection."""
        return self.conn

    def close(self):
        """Closes the SQLite database connection if open."""
        if self.conn:
            self.conn.close()
            self.conn = None
