"""
Unit tests for FinanceService — transaction CRUD, filtering, summaries, breakdown, and trends.
"""
import unittest
from tests.test_setup import FinanceTestCase


class TestFinanceService(FinanceTestCase):

    # ── add & summary ────────────────────────────────────────────────────────

    def test_add_income(self):
        """Adding an income transaction is reflected in the monthly summary income total."""
        self.finance_service.add_transaction(
            category_id=self.CAT_SALARY,
            type_="income",
            amount=50000.0,
            description="August Salary",
            date="2026-08-01"
        )
        summary = self.finance_service.get_monthly_summary(month=8, year=2026)
        self.assertAlmostEqual(summary["income"], 50000.0)
        self.assertAlmostEqual(summary["expense"], 0.0)
        self.assertAlmostEqual(summary["net_savings"], 50000.0)

    def test_add_expense(self):
        """Adding an expense decreases net savings; a larger expense makes net negative."""
        self.finance_service.add_transaction(
            category_id=self.CAT_SALARY,
            type_="income",
            amount=10000.0,
            description="Part-time income",
            date="2026-08-05"
        )
        self.finance_service.add_transaction(
            category_id=self.CAT_FOOD,
            type_="expense",
            amount=15000.0,
            description="Groceries",
            date="2026-08-10"
        )
        summary = self.finance_service.get_monthly_summary(month=8, year=2026)
        self.assertAlmostEqual(summary["income"], 10000.0)
        self.assertAlmostEqual(summary["expense"], 15000.0)
        self.assertAlmostEqual(summary["net_savings"], -5000.0)

    # ── delete ───────────────────────────────────────────────────────────────

    def test_delete_transaction(self):
        """A deleted transaction no longer appears in get_transactions()."""
        txn_id = self.finance_service.add_transaction(
            category_id=self.CAT_SALARY,
            type_="income",
            amount=5000.0,
            description="Bonus",
            date="2026-08-01"
        )
        self.assertEqual(len(self.finance_service.get_transactions()), 1)

        self.finance_service.delete_transaction(txn_id)
        self.assertEqual(len(self.finance_service.get_transactions()), 0)

    # ── filtering ────────────────────────────────────────────────────────────

    def test_filter_by_type(self):
        """Filtering transactions by type='income' returns only income rows."""
        self.finance_service.add_transaction(self.CAT_SALARY, "income", 30000.0, "Salary", "2026-08-01")
        self.finance_service.add_transaction(self.CAT_FOOD, "expense", 2000.0, "Food", "2026-08-05")
        self.finance_service.add_transaction(self.CAT_TRANSPORT, "expense", 500.0, "Bus", "2026-08-06")

        income_txns = self.finance_service.get_transactions(type_="income")
        expense_txns = self.finance_service.get_transactions(type_="expense")

        self.assertEqual(len(income_txns), 1)
        self.assertEqual(income_txns[0]["type"], "income")
        self.assertEqual(len(expense_txns), 2)
        self.assertTrue(all(t["type"] == "expense" for t in expense_txns))

    def test_filter_by_month(self):
        """Filtering by month=1 returns only January transactions, not February ones."""
        self.finance_service.add_transaction(self.CAT_SALARY, "income", 40000.0, "Jan Salary", "2026-01-01")
        self.finance_service.add_transaction(self.CAT_SALARY, "income", 40000.0, "Feb Salary", "2026-02-01")

        jan_txns = self.finance_service.get_transactions(month=1, year=2026)
        feb_txns = self.finance_service.get_transactions(month=2, year=2026)

        self.assertEqual(len(jan_txns), 1)
        self.assertEqual(jan_txns[0]["description"], "Jan Salary")
        self.assertEqual(len(feb_txns), 1)
        self.assertEqual(feb_txns[0]["description"], "Feb Salary")

    # ── category breakdown ───────────────────────────────────────────────────

    def test_category_breakdown(self):
        """Breakdown returns one entry per category with correct totals and non-zero percentages."""
        self.finance_service.add_transaction(self.CAT_FOOD, "expense", 3000.0, "Groceries", "2026-08-05")
        self.finance_service.add_transaction(self.CAT_TRANSPORT, "expense", 1000.0, "Commute", "2026-08-10")

        breakdown = self.finance_service.get_category_breakdown(month=8, year=2026, type_="expense")

        self.assertEqual(len(breakdown), 2)

        totals_map = {item["category_name"]: item["total"] for item in breakdown}
        self.assertAlmostEqual(totals_map["Food"], 3000.0)
        self.assertAlmostEqual(totals_map["Transport"], 1000.0)

        # Food = 75%, Transport = 25%
        pct_map = {item["category_name"]: item["percent"] for item in breakdown}
        self.assertAlmostEqual(pct_map["Food"], 75.0)
        self.assertAlmostEqual(pct_map["Transport"], 25.0)

    # ── trend data ───────────────────────────────────────────────────────────

    def test_trend_data(self):
        """get_trend_data(months=3) returns exactly 3 entries when data exists in 3 distinct months."""
        self.finance_service.add_transaction(self.CAT_SALARY, "income", 10000.0, "Jun income", "2026-06-01")
        self.finance_service.add_transaction(self.CAT_SALARY, "income", 20000.0, "Jul income", "2026-07-01")
        self.finance_service.add_transaction(self.CAT_SALARY, "income", 30000.0, "Aug income", "2026-08-01")

        trend = self.finance_service.get_trend_data(months=3)

        self.assertEqual(len(trend), 3)
        # Verify required keys exist
        for entry in trend:
            self.assertIn("month_label", entry)
            self.assertIn("income", entry)
            self.assertIn("expense", entry)
            self.assertIn("savings", entry)

        # Values should be correct (returned chronologically)
        income_values = [e["income"] for e in trend]
        self.assertIn(10000.0, income_values)
        self.assertIn(20000.0, income_values)
        self.assertIn(30000.0, income_values)

    # ── validation ───────────────────────────────────────────────────────────

    def test_add_transaction_invalid_amount(self):
        """Adding a transaction with amount <= 0 raises RuntimeError."""
        with self.assertRaises(RuntimeError):
            self.finance_service.add_transaction(
                self.CAT_SALARY, "income", -100.0, "Invalid", "2026-08-01"
            )


if __name__ == "__main__":
    unittest.main()
