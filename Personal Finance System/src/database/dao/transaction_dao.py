import sqlite3
from datetime import datetime

class TransactionDAO:
    """DAO for managing transaction CRUD and aggregation queries."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def insert(self, category_id: int, type_: str, amount: float, description: str, date: str) -> int:
        """Inserts a new transaction record."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (category_id, type, amount, description, date)
            VALUES (?, ?, ?, ?, ?);
        """, (category_id, type_, amount, description, date))
        self.conn.commit()
        return cursor.lastrowid

    def get_all(self, month: int = None, year: int = None, type_: str = None, category_id: int = None) -> list[dict]:
        """Retrieves transactions with optional filtering by month, year, type, or category."""
        cursor = self.conn.cursor()
        query = """
            SELECT t.id, t.category_id, t.type, t.amount, t.description, t.date, t.created_at,
                   c.name AS category_name, c.color AS category_color
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE 1=1
        """
        params = []

        if month is not None and year is not None:
            # Filter by YYYY-MM prefix or strftime
            month_str = f"{year:04d}-{month:02d}"
            query += " AND strftime('%Y-%m', t.date) = ?"
            params.append(month_str)
        elif year is not None:
            query += " AND strftime('%Y', t.date) = ?"
            params.append(str(year))

        if type_:
            query += " AND t.type = ?"
            params.append(type_)

        if category_id:
            query += " AND t.category_id = ?"
            params.append(category_id)

        query += " ORDER BY t.date DESC, t.id DESC;"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, transaction_id: int) -> dict | None:
        """Retrieves a single transaction by ID."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.id, t.category_id, t.type, t.amount, t.description, t.date, t.created_at,
                   c.name AS category_name, c.color AS category_color
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.id = ?;
        """, (transaction_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update(self, transaction_id: int, **fields) -> bool:
        """Updates specific fields of a transaction by ID."""
        if not fields:
            return False

        allowed_fields = {'category_id', 'type', 'amount', 'description', 'date'}
        set_clauses = []
        params = []

        for key, val in fields.items():
            if key in allowed_fields:
                set_clauses.append(f"{key} = ?")
                params.append(val)

        if not set_clauses:
            return False

        params.append(transaction_id)
        query = f"UPDATE transactions SET {', '.join(set_clauses)} WHERE id = ?;"

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount > 0

    def delete(self, transaction_id: int) -> bool:
        """Deletes a transaction by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?;", (transaction_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_monthly_totals(self, month: int, year: int) -> dict:
        """Returns total income and total expense for a given month and year."""
        cursor = self.conn.cursor()
        month_str = f"{year:04d}-{month:02d}"
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0.0) AS total_income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0.0) AS total_expense
            FROM transactions
            WHERE strftime('%Y-%m', date) = ?;
        """, (month_str,))
        row = cursor.fetchone()
        return {
            "income": float(row["total_income"]),
            "expense": float(row["total_expense"])
        }

    def get_category_totals(self, month: int, year: int, type_: str) -> list[dict]:
        """Returns total amount spent/earned per category for a given month and type."""
        cursor = self.conn.cursor()
        month_str = f"{year:04d}-{month:02d}"
        cursor.execute("""
            SELECT c.name AS category_name, c.color AS color, SUM(t.amount) AS total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.type = ? AND strftime('%Y-%m', t.date) = ?
            GROUP BY c.id, c.name, c.color
            ORDER BY total DESC;
        """, (type_, month_str))
        return [dict(row) for row in cursor.fetchall()]

    def get_recent(self, limit: int = 10) -> list[dict]:
        """Retrieves the N most recent transactions."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT t.id, t.category_id, t.type, t.amount, t.description, t.date,
                   c.name AS category_name, c.color AS category_color
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            ORDER BY t.date DESC, t.id DESC
            LIMIT ?;
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_trend(self, months: int = 6) -> list[dict]:
        """Returns monthly totals (income, expense) for the last N months ending at current date."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', date) AS month_key,
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0.0) AS income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0.0) AS expense
            FROM transactions
            GROUP BY month_key
            ORDER BY month_key DESC
            LIMIT ?;
        """, (months,))
        rows = cursor.fetchall()
        
        # Sort chronologically for charting
        result = [dict(row) for row in reversed(rows)]
        return result
