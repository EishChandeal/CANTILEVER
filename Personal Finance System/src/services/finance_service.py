import sqlite3
import calendar
from src.database.db_manager import DatabaseManager
from src.database.dao.transaction_dao import TransactionDAO

class FinanceService:
    """Business logic service for income and expense transactions."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.transaction_dao = TransactionDAO(db_manager.get_connection())

    def add_transaction(self, category_id: int, type_: str, amount: float, description: str, date: str) -> int:
        """Adds a new transaction."""
        try:
            if amount <= 0:
                raise ValueError("Amount must be greater than 0.")
            return self.transaction_dao.insert(category_id, type_, amount, description, date)
        except (sqlite3.Error, ValueError) as e:
            raise RuntimeError(f"Failed to add transaction: {str(e)}") from e

    def update_transaction(self, transaction_id: int, **fields) -> bool:
        """Updates fields of an existing transaction."""
        try:
            if 'amount' in fields and fields['amount'] <= 0:
                raise ValueError("Amount must be greater than 0.")
            return self.transaction_dao.update(transaction_id, **fields)
        except (sqlite3.Error, ValueError) as e:
            raise RuntimeError(f"Failed to update transaction: {str(e)}") from e

    def delete_transaction(self, transaction_id: int) -> bool:
        """Deletes a transaction by ID."""
        try:
            return self.transaction_dao.delete(transaction_id)
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to delete transaction: {str(e)}") from e

    def get_transactions(self, month: int = None, year: int = None, type_: str = None, category_id: int = None) -> list[dict]:
        """Retrieves transactions matching optional filters."""
        try:
            return self.transaction_dao.get_all(month=month, year=year, type_=type_, category_id=category_id)
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch transactions: {str(e)}") from e

    def get_recent_transactions(self, limit: int = 10) -> list[dict]:
        """Retrieves the N most recent transactions."""
        try:
            return self.transaction_dao.get_recent(limit=limit)
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch recent transactions: {str(e)}") from e

    def get_monthly_summary(self, month: int, year: int) -> dict:
        """Returns total income, total expenses, and net savings for a given month."""
        try:
            totals = self.transaction_dao.get_monthly_totals(month, year)
            income = totals["income"]
            expense = totals["expense"]
            net_savings = income - expense
            return {
                "income": income,
                "expense": expense,
                "net_savings": net_savings
            }
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to calculate monthly summary: {str(e)}") from e

    def get_category_breakdown(self, month: int, year: int, type_: str) -> list[dict]:
        """Returns category totals and percent contribution for a given month and transaction type."""
        try:
            category_totals = self.transaction_dao.get_category_totals(month, year, type_)
            overall_total = sum(c["total"] for c in category_totals)

            for cat in category_totals:
                cat["percent"] = round((cat["total"] / overall_total * 100), 1) if overall_total > 0 else 0.0

            return category_totals
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch category breakdown: {str(e)}") from e

    def get_trend_data(self, months: int = 6) -> list[dict]:
        """Returns monthly income, expense, and net savings trend over the past N months."""
        try:
            raw_trend = self.transaction_dao.get_trend(months=months)
            trend_list = []
            for item in raw_trend:
                month_key = item["month_key"]  # 'YYYY-MM'
                y_str, m_str = month_key.split('-')
                month_label = f"{calendar.month_abbr[int(m_str)]} '{y_str[2:]}"
                
                income = item["income"]
                expense = item["expense"]
                savings = income - expense
                
                trend_list.append({
                    "month_key": month_key,
                    "month_label": month_label,
                    "income": income,
                    "expense": expense,
                    "savings": savings
                })
            return trend_list
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch trend data: {str(e)}") from e
