import sqlite3

class CategoryDAO:
    """DAO for managing category operations in SQLite database."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_all(self) -> list[dict]:
        """Fetches all categories."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY type DESC, name ASC;")
        return [dict(row) for row in cursor.fetchall()]

    def get_by_type(self, category_type: str) -> list[dict]:
        """Fetches categories by type ('income' or 'expense')."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM categories WHERE type = ? ORDER BY name ASC;",
            (category_type,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def insert(self, name: str, category_type: str, color: str = "#3b82f6") -> int:
        """Inserts a new category and returns its ID."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO categories (name, type, color) VALUES (?, ?, ?);",
            (name.strip(), category_type.strip(), color)
        )
        self.conn.commit()
        return cursor.lastrowid

    def delete(self, category_id: int) -> bool:
        """Deletes a category if it has no associated transactions. Returns True if deleted."""
        cursor = self.conn.cursor()
        # Check if transactions exist for this category
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE category_id = ?;", (category_id,))
        if cursor.fetchone()[0] > 0:
            return False

        cursor.execute("DELETE FROM categories WHERE id = ?;", (category_id,))
        self.conn.commit()
        return cursor.rowcount > 0
