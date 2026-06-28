from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from datetime import date
from .models import Group, Expense, ExpenseSplit, Settlement, Budget

class ModelTests(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(username='alice', email='alice@example.com', password='password123')
        self.user2 = User.objects.create_user(username='bob', email='bob@example.com', password='password123')
        self.user3 = User.objects.create_user(username='charlie', email='charlie@example.com', password='password123')

        # Create a test group
        self.group = Group.objects.create(
            name='Trip to Goa',
            description='Vacation expenses',
            created_by=self.user1
        )
        self.group.members.add(self.user1, self.user2, self.user3)

    def test_group_creation(self):
        self.assertEqual(self.group.name, 'Trip to Goa')
        self.assertEqual(self.group.members.count(), 3)
        self.assertEqual(str(self.group), 'Trip to Goa')

    def test_expense_creation(self):
        expense = Expense.objects.create(
            group=self.group,
            description='Dinner bill',
            amount=90.00,
            paid_by=self.user1,
            date=date.today()
        )
        self.assertEqual(expense.description, 'Dinner bill')
        self.assertEqual(expense.amount, 90.00)
        self.assertEqual(str(expense), f"Dinner bill - 90.00 in Trip to Goa")

    def test_expense_split(self):
        expense = Expense.objects.create(
            group=self.group,
            description='Dinner bill',
            amount=90.00,
            paid_by=self.user1,
            date=date.today()
        )
        # Create splits
        split1 = ExpenseSplit.objects.create(expense=expense, user=self.user1, amount=30.00)
        split2 = ExpenseSplit.objects.create(expense=expense, user=self.user2, amount=30.00)
        split3 = ExpenseSplit.objects.create(expense=expense, user=self.user3, amount=30.00)

        self.assertEqual(expense.splits.count(), 3)
        self.assertEqual(split1.amount, 30.00)
        self.assertEqual(str(split1), "alice owes 30.00 for Dinner bill")

        # Test unique_together constraint on (expense, user)
        with self.assertRaises(IntegrityError):
            ExpenseSplit.objects.create(expense=expense, user=self.user1, amount=10.00)

    def test_settlement(self):
        settlement = Settlement.objects.create(
            group=self.group,
            payer=self.user2,
            payee=self.user1,
            amount=30.00,
            status='completed'
        )
        self.assertEqual(settlement.payer, self.user2)
        self.assertEqual(settlement.payee, self.user1)
        self.assertEqual(settlement.amount, 30.00)
        self.assertEqual(settlement.status, 'completed')
        self.assertEqual(str(settlement), "bob paid alice 30.00 in Trip to Goa")

    def test_budget_creation(self):
        # Create group budget
        group_budget = Budget.objects.create(
            group=self.group,
            amount_limit=500.00
        )
        self.assertEqual(group_budget.amount_limit, 500.00)
        self.assertEqual(str(group_budget), "Budget of 500.00 for group Trip to Goa")

        # Create personal budget
        user_budget = Budget.objects.create(
            user=self.user1,
            amount_limit=100.00
        )
        self.assertEqual(user_budget.amount_limit, 100.00)
        self.assertEqual(str(user_budget), "Personal budget of 100.00 for alice")

