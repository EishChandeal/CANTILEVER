import sqlite3
from src.database.db_manager import DatabaseManager
from src.database.dao.category_dao import CategoryDAO

class SettingsService:
    """Business logic service for app configuration, currency settings, and category management."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.conn = db_manager.get_connection()
        self.category_dao = CategoryDAO(self.conn)

    def get(self, key: str, default: str = None) -> str:
        """Retrieves a configuration value by key."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?;", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch setting '{key}': {str(e)}") from e

    def set(self, key: str, value: str):
        """Sets or updates a configuration key-value pair."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value;
            """, (key, str(value)))
            self.conn.commit()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to set configuration '{key}': {str(e)}") from e

    def get_currency_symbol(self) -> str:
        """Returns the configured currency symbol (defaults to ₹)."""
        return self.get("currency_symbol", default="₹")

    def get_all_categories(self) -> list[dict]:
        """Retrieves all categories."""
        try:
            return self.category_dao.get_all()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch categories: {str(e)}") from e

    def add_category(self, name: str, category_type: str, color: str = "#3b82f6") -> int:
        """Adds a new income/expense category."""
        try:
            if not name or not name.strip():
                raise ValueError("Category name cannot be empty.")
            return self.category_dao.insert(name, category_type, color)
        except (sqlite3.Error, ValueError) as e:
            raise RuntimeError(f"Failed to add category: {str(e)}") from e

    def delete_category(self, category_id: int) -> bool:
        """Deletes a category if unused. Returns False if category has transactions."""
        try:
            return self.category_dao.delete(category_id)
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to delete category: {str(e)}") from e
