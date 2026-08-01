"""
Base test setup with in-memory SQLite DB.
All test classes inherit from FinanceTestCase for a clean, isolated environment.
"""
import sqlite3
import sys
import unittest
from pathlib import Path

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database.schema import initialize_db
from src.database.dao.transaction_dao import TransactionDAO
from src.database.dao.category_dao import CategoryDAO
from src.database.dao.budget_dao import BudgetDAO
from src.database.dao.savings_dao import SavingsDAO
from src.services.finance_service import FinanceService
from src.services.budget_service import BudgetService
from src.services.savings_service import SavingsService
from src.services.settings_service import SettingsService


class InMemoryDB:
    """Lightweight in-memory database manager compatible with the real DatabaseManager interface."""

    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        initialize_db(self.conn)

    def get_connection(self) -> sqlite3.Connection:
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None


class FinanceTestCase(unittest.TestCase):
    """Base TestCase that provisions a fresh in-memory DB and all service instances."""

    # Known IDs seeded by initialize_db (income first, then expense)
    CAT_SALARY = 1       # income
    CAT_FREELANCE = 2    # income
    CAT_FOOD = 5         # expense
    CAT_TRANSPORT = 6    # expense
    CAT_RENT = 7         # expense

    def setUp(self):
        """Create fresh in-memory DB, DAOs, and services before every test."""
        self.db = InMemoryDB()
        conn = self.db.get_connection()

        # DAOs
        self.transaction_dao = TransactionDAO(conn)
        self.category_dao = CategoryDAO(conn)
        self.budget_dao = BudgetDAO(conn)
        self.savings_dao = SavingsDAO(conn)

        # Services
        self.finance_service = FinanceService(self.db)
        self.budget_service = BudgetService(self.db)
        self.savings_service = SavingsService(self.db)
        self.settings_service = SettingsService(self.db)

    def tearDown(self):
        """Close the in-memory connection after every test."""
        self.db.close()
