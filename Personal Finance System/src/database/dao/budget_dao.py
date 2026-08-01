import sqlite3

class BudgetDAO:
    """DAO for managing monthly category budgets in SQLite database."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def set_budget(self, category_id: int, month: int, year: int, limit_amount: float) -> int:
        """Inserts or updates a monthly budget limit for a category."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO budgets (category_id, month, year, limit_amount)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(category_id, month, year) 
            DO UPDATE SET limit_amount = excluded.limit_amount;
        """, (category_id, month, year, limit_amount))
        self.conn.commit()
        return cursor.lastrowid

    def get_by_month_year(self, month: int, year: int) -> list[dict]:
        """Retrieves budgets for a specific month and year joined with category information."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT b.id, b.category_id, b.month, b.year, b.limit_amount,
                   c.name AS category_name, c.color AS category_color
            FROM budgets b
            JOIN categories c ON b.category_id = c.id
            WHERE b.month = ? AND b.year = ?
            ORDER BY c.name ASC;
        """, (month, year))
        return [dict(row) for row in cursor.fetchall()]

    def delete(self, budget_id: int) -> bool:
        """Deletes a budget by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM budgets WHERE id = ?;", (budget_id,))
        self.conn.commit()
        return cursor.rowcount > 0
