import sqlite3
from src.database.db_manager import DatabaseManager
from src.database.dao.savings_dao import SavingsDAO

class SavingsService:
    """Business logic service for savings goals management."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.savings_dao = SavingsDAO(db_manager.get_connection())

    def create_goal(self, name: str, target_amount: float, deadline: str = None) -> int:
        """Creates a new savings goal."""
        try:
            if target_amount <= 0:
                raise ValueError("Target amount must be greater than 0.")
            return self.savings_dao.insert(name, target_amount, deadline)
        except (sqlite3.Error, ValueError) as e:
            raise RuntimeError(f"Failed to create savings goal: {str(e)}") from e

    def add_funds(self, goal_id: int, amount: float) -> bool:
        """Adds funds to an existing savings goal. Auto-completes goal if target is reached."""
        try:
            if amount <= 0:
                raise ValueError("Contribution amount must be greater than 0.")

            goals = self.savings_dao.get_all()
            target_goal = next((g for g in goals if g["id"] == goal_id), None)
            
            if not target_goal:
                raise ValueError("Savings goal not found.")

            new_amount = target_goal["current_amount"] + amount
            self.savings_dao.update_amount(goal_id, new_amount)

            if new_amount >= target_goal["target_amount"]:
                self.savings_dao.set_status(goal_id, "completed")

            return True
        except (sqlite3.Error, ValueError) as e:
            raise RuntimeError(f"Failed to add funds to savings goal: {str(e)}") from e

    def get_all_goals(self) -> list[dict]:
        """Retrieves all savings goals with completion percentage."""
        try:
            return self.savings_dao.get_all()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to fetch savings goals: {str(e)}") from e

    def complete_goal(self, goal_id: int) -> bool:
        """Marks a savings goal as completed."""
        try:
            return self.savings_dao.set_status(goal_id, "completed")
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to complete savings goal: {str(e)}") from e

    def delete_goal(self, goal_id: int) -> bool:
        """Deletes a savings goal by ID."""
        try:
            return self.savings_dao.delete(goal_id)
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to delete savings goal: {str(e)}") from e
