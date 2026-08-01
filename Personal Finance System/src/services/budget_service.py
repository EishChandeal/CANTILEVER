import sqlite3
from src.database.db_manager import DatabaseManager
from src.database.dao.budget_dao import BudgetDAO
from src.database.dao.transaction_dao import TransactionDAO

class BudgetService:
    """Business logic service for category budget tracking and alerts."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.budget_dao = BudgetDAO(db_manager.get_connection())
        self.transaction_dao = TransactionDAO(db_manager.get_connection())

    def set_budget(self, category_id: int, month: int, year: int, limit_amount: float) -> int:
        """Sets or updates a monthly budget limit for a category."""
        try:
            if limit_amount <= 0:
                raise ValueError("Budget limit must be greater than 0.")
            return self.budget_dao.set_budget(category_id, month, year, limit_amount)
        except (sqlite3.Error, ValueError) as e:
            raise RuntimeError(f"Failed to set budget: {str(e)}") from e

    def get_budget_vs_actual(self, month: int, year: int) -> list[dict]:
        """Calculates actual spending vs budget limit for each category in a month."""
        try:
            budgets = self.budget_dao.get_by_month_year(month, year)
            actual_expenses = self.transaction_dao.get_category_totals(month, year, type_="expense")
            
            # Map spending by category_name
            spent_map = {item["category_name"]: item["total"] for item in actual_expenses}

            result = []
            for b in budgets:
                cat_id = b["category_id"]
                cat_name = b["category_name"]
                color = b["category_color"]
                limit = b["limit_amount"]
                spent = spent_map.get(cat_name, 0.0)
                remaining = limit - spent
                percent_used = round((spent / limit * 100), 1) if limit > 0 else 0.0

                result.append({
                    "id": b["id"],
                    "category_id": cat_id,
                    "category_name": cat_name,
                    "color": color,
                    "budget": limit,
                    "spent": spent,
                    "remaining": remaining,
                    "percent_used": percent_used
                })

            return result
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch budget vs actual comparison: {str(e)}") from e

    def get_over_budget_alerts(self, month: int, year: int) -> list[dict]:
        """Returns categories where spending has exceeded 80% of the budget limit."""
        try:
            comparison = self.get_budget_vs_actual(month, year)
            return [item for item in comparison if item["percent_used"] >= 80.0]
        except Exception as e:
            raise RuntimeError(f"Failed to check budget alerts: {str(e)}") from e
