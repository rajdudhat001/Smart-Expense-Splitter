from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse
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


class AuthenticationTests(TestCase):
    def setUp(self):
        # Create a test user for login scenarios
        self.username = 'testuser'
        self.email = 'testuser@example.com'
        self.password = 'SecurePassword123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)
        
        # Define URLs
        self.login_url = reverse('login')
        self.register_url = reverse('register')
        self.logout_url = reverse('logout')
        self.dashboard_url = reverse('dashboard')

    def test_register_page_loads(self):
        """Test if registration page loads successfully."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/register.html')

    def test_registration_successful(self):
        """Test registering a new user with valid inputs."""
        payload = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password999',
            'confirm_password': 'Password999'
        }
        response = self.client.post(self.register_url, data=payload)
        # Should redirect to the login page on success
        self.assertRedirects(response, self.login_url)
        # Check if new user actually exists in the database
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_registration_mismatched_passwords(self):
        """Test that passwords mismatch validation shows an error."""
        payload = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Password999',
            'confirm_password': 'DifferentPassword'
        }
        response = self.client.post(self.register_url, data=payload)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_password', form.errors)
        self.assertIn("Passwords do not match.", form.errors['confirm_password'][0])

    def test_registration_duplicate_email(self):
        """Test that duplicate email validation shows an error."""
        payload = {
            'username': 'uniqueusername',
            'email': self.email,  # Already taken by setUp
            'password': 'Password999',
            'confirm_password': 'Password999'
        }
        response = self.client.post(self.register_url, data=payload)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn("Email is already registered.", form.errors['email'][0])

    def test_login_page_loads(self):
        """Test if login page loads successfully."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/login.html')

    def test_login_successful(self):
        """Test logging in with correct credentials."""
        payload = {
            'username': self.username,
            'password': self.password
        }
        response = self.client.post(self.login_url, data=payload)
        # Success should redirect to dashboard
        self.assertRedirects(response, self.dashboard_url)

    def test_login_invalid_credentials(self):
        """Test that incorrect credentials display error messages."""
        payload = {
            'username': self.username,
            'password': 'WrongPassword123'
        }
        response = self.client.post(self.login_url, data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password.")

    def test_dashboard_requires_login(self):
        """Test that accessing the dashboard without logging in redirects to login page."""
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.dashboard_url}")

    def test_dashboard_accessible_when_logged_in(self):
        """Test dashboard loads when logged in."""
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/dashboard.html')
        self.assertContains(response, f"Welcome to Smart Expense Splitter, {self.username}!")

    def test_logout_redirects_to_login(self):
        """Test logout clears the session and redirects to login."""
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.login_url)
