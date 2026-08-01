"""
Unit tests for BudgetService — setting budgets, actual vs budget calculation, and alerts.
"""
import unittest
from tests.test_setup import FinanceTestCase


class TestBudgetService(FinanceTestCase):

    # ── set / get ────────────────────────────────────────────────────────────

    def test_set_budget(self):
        """A newly set budget is retrievable via get_by_month_year with correct limit."""
        self.budget_service.set_budget(
            category_id=self.CAT_FOOD,
            month=8,
            year=2026,
            limit_amount=5000.0
        )
        budgets = self.budget_dao.get_by_month_year(month=8, year=2026)

        self.assertEqual(len(budgets), 1)
        self.assertEqual(budgets[0]["category_id"], self.CAT_FOOD)
        self.assertAlmostEqual(budgets[0]["limit_amount"], 5000.0)

    # ── budget vs actual ─────────────────────────────────────────────────────

    def test_get_budget_vs_actual(self):
        """Spending ₹600 against a ₹1000 budget should yield 60.0 percent_used."""
        self.budget_service.set_budget(self.CAT_FOOD, month=8, year=2026, limit_amount=1000.0)
        self.finance_service.add_transaction(
            category_id=self.CAT_FOOD,
            type_="expense",
            amount=600.0,
            description="Groceries",
            date="2026-08-10"
        )

        result = self.budget_service.get_budget_vs_actual(month=8, year=2026)

        self.assertEqual(len(result), 1)
        entry = result[0]
        self.assertAlmostEqual(entry["budget"], 1000.0)
        self.assertAlmostEqual(entry["spent"], 600.0)
        self.assertAlmostEqual(entry["remaining"], 400.0)
        self.assertAlmostEqual(entry["percent_used"], 60.0)

    # ── over-budget alerts ───────────────────────────────────────────────────

    def test_over_budget_alert(self):
        """Spending ₹900 against ₹1000 budget triggers an alert (percent_used ≥ 80)."""
        self.budget_service.set_budget(self.CAT_TRANSPORT, month=8, year=2026, limit_amount=1000.0)
        self.finance_service.add_transaction(
            category_id=self.CAT_TRANSPORT,
            type_="expense",
            amount=900.0,
            description="Fuel",
            date="2026-08-12"
        )

        alerts = self.budget_service.get_over_budget_alerts(month=8, year=2026)

        self.assertEqual(len(alerts), 1)
        self.assertAlmostEqual(alerts[0]["percent_used"], 90.0)
        self.assertEqual(alerts[0]["category_name"], "Transport")

    def test_no_alert_below_threshold(self):
        """Spending below 80% of budget should NOT trigger an alert."""
        self.budget_service.set_budget(self.CAT_FOOD, month=8, year=2026, limit_amount=1000.0)
        self.finance_service.add_transaction(
            category_id=self.CAT_FOOD,
            type_="expense",
            amount=500.0,
            description="Groceries",
            date="2026-08-05"
        )

        alerts = self.budget_service.get_over_budget_alerts(month=8, year=2026)
        self.assertEqual(len(alerts), 0)

    # ── upsert ───────────────────────────────────────────────────────────────

    def test_upsert_budget(self):
        """Setting a budget twice for the same category/month updates it; only one row exists."""
        self.budget_service.set_budget(self.CAT_RENT, month=8, year=2026, limit_amount=10000.0)
        self.budget_service.set_budget(self.CAT_RENT, month=8, year=2026, limit_amount=12000.0)

        budgets = self.budget_dao.get_by_month_year(month=8, year=2026)
        # Only one row for that category/month pair
        rent_budgets = [b for b in budgets if b["category_id"] == self.CAT_RENT]
        self.assertEqual(len(rent_budgets), 1)
        # Updated to the latest value
        self.assertAlmostEqual(rent_budgets[0]["limit_amount"], 12000.0)

    def test_multiple_category_budgets(self):
        """Two different categories can each have their own budget for the same month."""
        self.budget_service.set_budget(self.CAT_FOOD, month=8, year=2026, limit_amount=3000.0)
        self.budget_service.set_budget(self.CAT_TRANSPORT, month=8, year=2026, limit_amount=1500.0)

        budgets = self.budget_dao.get_by_month_year(month=8, year=2026)
        self.assertEqual(len(budgets), 2)

    def test_budget_with_zero_spending(self):
        """A category with a budget but no transactions should show 0% spent."""
        self.budget_service.set_budget(self.CAT_FOOD, month=8, year=2026, limit_amount=5000.0)

        result = self.budget_service.get_budget_vs_actual(month=8, year=2026)
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0]["spent"], 0.0)
        self.assertAlmostEqual(result[0]["percent_used"], 0.0)

    def test_set_budget_invalid_amount(self):
        """Setting a budget with limit_amount <= 0 raises RuntimeError."""
        with self.assertRaises(RuntimeError):
            self.budget_service.set_budget(self.CAT_FOOD, month=8, year=2026, limit_amount=0.0)


if __name__ == "__main__":
    unittest.main()
