"""
Unit tests for SavingsService — goal creation, fund deposits, auto-completion, and percentages.
"""
import unittest
from tests.test_setup import FinanceTestCase


class TestSavingsService(FinanceTestCase):

    # ── create goal ──────────────────────────────────────────────────────────

    def test_create_goal(self):
        """A new goal starts with current_amount=0.0 and status='active'."""
        goal_id = self.savings_service.create_goal(
            name="Emergency Fund",
            target_amount=100000.0,
            deadline="2027-03-01"
        )
        self.assertIsNotNone(goal_id)
        self.assertGreater(goal_id, 0)

        goals = self.savings_service.get_all_goals()
        self.assertEqual(len(goals), 1)

        goal = goals[0]
        self.assertEqual(goal["name"], "Emergency Fund")
        self.assertAlmostEqual(goal["target_amount"], 100000.0)
        self.assertAlmostEqual(goal["current_amount"], 0.0)
        self.assertEqual(goal["status"], "active")

    # ── add funds ────────────────────────────────────────────────────────────

    def test_add_funds(self):
        """Depositing money correctly increases current_amount without triggering completion."""
        goal_id = self.savings_service.create_goal("New Laptop", 50000.0, None)
        self.savings_service.add_funds(goal_id, 15000.0)

        goals = self.savings_service.get_all_goals()
        goal = next(g for g in goals if g["id"] == goal_id)

        self.assertAlmostEqual(goal["current_amount"], 15000.0)
        self.assertEqual(goal["status"], "active")  # Not completed yet

    def test_add_funds_multiple_deposits(self):
        """Multiple deposits accumulate correctly."""
        goal_id = self.savings_service.create_goal("Vacation", 20000.0, None)
        self.savings_service.add_funds(goal_id, 5000.0)
        self.savings_service.add_funds(goal_id, 8000.0)

        goals = self.savings_service.get_all_goals()
        goal = next(g for g in goals if g["id"] == goal_id)

        self.assertAlmostEqual(goal["current_amount"], 13000.0)
        self.assertEqual(goal["status"], "active")

    # ── auto-complete ────────────────────────────────────────────────────────

    def test_auto_complete(self):
        """When deposited amount equals target, goal status automatically changes to 'completed'."""
        goal_id = self.savings_service.create_goal("New Phone", 500.0, None)
        self.savings_service.add_funds(goal_id, 500.0)

        goals = self.savings_service.get_all_goals()
        goal = next(g for g in goals if g["id"] == goal_id)

        self.assertEqual(goal["status"], "completed")
        self.assertAlmostEqual(goal["current_amount"], 500.0)

    def test_auto_complete_when_overfunded(self):
        """Depositing more than the target also triggers auto-completion."""
        goal_id = self.savings_service.create_goal("Holiday", 1000.0, None)
        self.savings_service.add_funds(goal_id, 1500.0)  # Overfunded

        goals = self.savings_service.get_all_goals()
        goal = next(g for g in goals if g["id"] == goal_id)

        self.assertEqual(goal["status"], "completed")
        self.assertAlmostEqual(goal["current_amount"], 1500.0)

    # ── percent_complete ─────────────────────────────────────────────────────

    def test_percent_complete(self):
        """With target=1000 and current=250, percent_complete should be 25.0."""
        goal_id = self.savings_service.create_goal("Bike", 1000.0, None)
        self.savings_service.add_funds(goal_id, 250.0)

        goals = self.savings_service.get_all_goals()
        goal = next(g for g in goals if g["id"] == goal_id)

        self.assertAlmostEqual(goal["percent_complete"], 25.0)

    def test_percent_complete_zero(self):
        """A brand new goal with no deposits has 0% completion."""
        goal_id = self.savings_service.create_goal("Car", 500000.0, None)

        goals = self.savings_service.get_all_goals()
        goal = next(g for g in goals if g["id"] == goal_id)

        self.assertAlmostEqual(goal["percent_complete"], 0.0)

    def test_percent_complete_full(self):
        """A fully funded goal reports 100% completion."""
        goal_id = self.savings_service.create_goal("Watch", 2000.0, None)
        self.savings_service.add_funds(goal_id, 2000.0)

        goals = self.savings_service.get_all_goals()
        goal = next(g for g in goals if g["id"] == goal_id)

        self.assertAlmostEqual(goal["percent_complete"], 100.0)

    # ── manual complete & delete ─────────────────────────────────────────────

    def test_manual_complete(self):
        """complete_goal() sets status to 'completed' regardless of current_amount."""
        goal_id = self.savings_service.create_goal("Study Fund", 30000.0, None)
        self.savings_service.complete_goal(goal_id)

        goals = self.savings_service.get_all_goals()
        goal = next(g for g in goals if g["id"] == goal_id)
        self.assertEqual(goal["status"], "completed")

    def test_delete_goal(self):
        """Deleting a goal removes it from get_all_goals()."""
        goal_id = self.savings_service.create_goal("Temp Goal", 5000.0, None)
        self.assertEqual(len(self.savings_service.get_all_goals()), 1)

        self.savings_service.delete_goal(goal_id)
        self.assertEqual(len(self.savings_service.get_all_goals()), 0)

    # ── validation ───────────────────────────────────────────────────────────

    def test_create_goal_invalid_target(self):
        """Creating a goal with target_amount <= 0 raises RuntimeError."""
        with self.assertRaises(RuntimeError):
            self.savings_service.create_goal("Bad Goal", -100.0, None)

    def test_add_funds_invalid_amount(self):
        """Depositing 0 or negative raises RuntimeError."""
        goal_id = self.savings_service.create_goal("Valid Goal", 10000.0, None)
        with self.assertRaises(RuntimeError):
            self.savings_service.add_funds(goal_id, 0.0)


if __name__ == "__main__":
    unittest.main()
