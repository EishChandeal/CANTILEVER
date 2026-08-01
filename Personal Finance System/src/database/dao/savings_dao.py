import sqlite3

class SavingsDAO:
    """DAO for managing savings goals in SQLite database."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def insert(self, name: str, target_amount: float, deadline: str = None) -> int:
        """Inserts a new savings goal."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO savings_goals (name, target_amount, current_amount, deadline, status)
            VALUES (?, ?, 0.0, ?, 'active');
        """, (name.strip(), target_amount, deadline))
        self.conn.commit()
        return cursor.lastrowid

    def get_all(self) -> list[dict]:
        """Retrieves all savings goals with calculated completion percentages."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, target_amount, current_amount, deadline, status, created_at
            FROM savings_goals
            ORDER BY status ASC, created_at DESC;
        """)
        goals = []
        for row in cursor.fetchall():
            g = dict(row)
            target = g['target_amount']
            current = g['current_amount']
            g['percent_complete'] = round((current / target * 100), 1) if target > 0 else 0.0
            goals.append(g)
        return goals

    def update_amount(self, goal_id: int, new_amount: float) -> bool:
        """Updates the accumulated current amount for a savings goal."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE savings_goals 
            SET current_amount = ?
            WHERE id = ?;
        """, (new_amount, goal_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def set_status(self, goal_id: int, status: str) -> bool:
        """Sets the status ('active' or 'completed') of a savings goal."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE savings_goals 
            SET status = ?
            WHERE id = ?;
        """, (status, goal_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def delete(self, goal_id: int) -> bool:
        """Deletes a savings goal by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM savings_goals WHERE id = ?;", (goal_id,))
        self.conn.commit()
        return cursor.rowcount > 0
