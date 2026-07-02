from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.urls import reverse
from datetime import date
from .models import Group, Expense, ExpenseSplit, Settlement, Budget, Member

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

        # Create a member for paid_by checks
        self.member1 = Member.objects.create(
            group=self.group,
            name='Alice Member',
            email='alice@example.com'
        )

    def test_group_creation(self):
        self.assertEqual(self.group.name, 'Trip to Goa')
        self.assertEqual(self.group.members.count(), 3)
        self.assertEqual(str(self.group), 'Trip to Goa')

    def test_expense_creation(self):
        expense = Expense.objects.create(
            group=self.group,
            title='Dinner bill',
            amount=90.00,
            paid_by=self.member1,
            date=date.today(),
            category='Food',
            created_by=self.user1
        )
        self.assertEqual(expense.title, 'Dinner bill')
        self.assertEqual(expense.amount, 90.00)
        self.assertEqual(str(expense), f"Dinner bill - 90.00 in Trip to Goa")

    def test_expense_split(self):
        expense = Expense.objects.create(
            group=self.group,
            title='Dinner bill',
            amount=90.00,
            paid_by=self.member1,
            date=date.today(),
            category='Food',
            created_by=self.user1
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


class GroupCRUDTests(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='alice', email='alice@example.com', password='password123')
        self.user2 = User.objects.create_user(username='bob', email='bob@example.com', password='password123')

        # Create a group owned by alice
        self.group = Group.objects.create(
            name='Alice Goa Trip',
            description='Trip to Goa funded by Alice',
            created_by=self.user1
        )
        self.group.members.add(self.user1)

        # URLs
        self.list_url = reverse('group_list')
        self.create_url = reverse('group_create')
        self.update_url = reverse('group_update', args=[self.group.pk])
        self.delete_url = reverse('group_delete', args=[self.group.pk])
        self.login_url = reverse('login')

    def test_group_pages_require_login(self):
        """Verify unauthenticated users cannot access any group pages."""
        # List page
        response = self.client.get(self.list_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.list_url}")

        # Create page GET/POST
        response = self.client.get(self.create_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.create_url}")

        response = self.client.post(self.create_url, data={'name': 'New Group'})
        self.assertRedirects(response, f"{self.login_url}?next={self.create_url}")

        # Update page GET/POST
        response = self.client.get(self.update_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.update_url}")

        response = self.client.post(self.update_url, data={'name': 'Updated Group'})
        self.assertRedirects(response, f"{self.login_url}?next={self.update_url}")

        # Delete page GET/POST
        response = self.client.get(self.delete_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.delete_url}")

        response = self.client.post(self.delete_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.delete_url}")

    def test_group_list_only_shows_owned_groups(self):
        """Verify logged-in user only sees the groups they created."""
        # Log in as Alice (creator of Alice Goa Trip)
        self.client.login(username='alice', password='password123')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Goa Trip')

        # Log in as Bob (who has no groups)
        self.client.login(username='bob', password='password123')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Alice Goa Trip')

    def test_group_create_success(self):
        """Verify creating a group works, sets owner and member, and redirects."""
        self.client.login(username='bob', password='password123')
        payload = {
            'name': 'Bob Party Group',
            'description': 'Party weekend description'
        }
        response = self.client.post(self.create_url, data=payload)
        self.assertRedirects(response, self.list_url)
        
        # Verify database creation
        new_group = Group.objects.get(name='Bob Party Group')
        self.assertEqual(new_group.created_by, self.user2)
        self.assertIn(self.user2, new_group.members.all())

    def test_group_create_validation_error(self):
        """Verify validation fails if group name is too short."""
        self.client.login(username='bob', password='password123')
        payload = {
            'name': 'B',  # too short
            'description': 'Short name'
        }
        response = self.client.post(self.create_url, data=payload)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn("Group name must be at least 3 characters long.", form.errors['name'][0])

    def test_group_update_success(self):
        """Verify group creator can update details."""
        self.client.login(username='alice', password='password123')
        payload = {
            'name': 'Alice Goa Trip V2',
            'description': 'Updated description text'
        }
        response = self.client.post(self.update_url, data=payload)
        self.assertRedirects(response, self.list_url)
        
        # Verify db updates
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, 'Alice Goa Trip V2')
        self.assertEqual(self.group.description, 'Updated description text')

    def test_group_update_and_delete_unauthorized(self):
        """Verify non-creator gets 404 when editing or deleting group."""
        self.client.login(username='bob', password='password123')
        
        # Edit GET/POST
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(self.update_url, data={'name': 'Hacked Group'})
        self.assertEqual(response.status_code, 404)

        # Delete GET/POST
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 404)

        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 404)
        
        # Verify group is not deleted
        self.assertTrue(Group.objects.filter(pk=self.group.pk).exists())

    def test_group_delete_success(self):
        """Verify group creator can delete group."""
        self.client.login(username='alice', password='password123')
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, self.list_url)
        # Verify database record is gone
        self.assertFalse(Group.objects.filter(pk=self.group.pk).exists())


class MemberCRUDTests(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='alice', email='alice@example.com', password='password123')
        self.user2 = User.objects.create_user(username='bob', email='bob@example.com', password='password123')

        # Create groups
        self.group = Group.objects.create(
            name='Alice Goa Trip',
            description='Trip to Goa funded by Alice',
            created_by=self.user1
        )
        self.group.members.add(self.user1)

        self.member = Member.objects.create(
            group=self.group,
            name='John Doe',
            email='john@example.com',
            phone='1234567890'
        )

        # URLs
        self.list_url = reverse('member_list', args=[self.group.pk])
        self.create_url = reverse('member_create', args=[self.group.pk])
        self.update_url = reverse('member_update', args=[self.group.pk, self.member.pk])
        self.delete_url = reverse('member_delete', args=[self.group.pk, self.member.pk])
        self.login_url = reverse('login')

    def test_member_pages_require_login(self):
        """Verify unauthenticated users cannot access member pages."""
        # List
        response = self.client.get(self.list_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.list_url}")

        # Create GET/POST
        response = self.client.get(self.create_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.create_url}")

        response = self.client.post(self.create_url, data={'name': 'Jane Doe'})
        self.assertRedirects(response, f"{self.login_url}?next={self.create_url}")

        # Update GET/POST
        response = self.client.get(self.update_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.update_url}")

        response = self.client.post(self.update_url, data={'name': 'John Doe Updated'})
        self.assertRedirects(response, f"{self.login_url}?next={self.update_url}")

        # Delete GET/POST
        response = self.client.get(self.delete_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.delete_url}")

        response = self.client.post(self.delete_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.delete_url}")

    def test_member_pages_unauthorized(self):
        """Verify non-creator of group cannot access group member management pages."""
        self.client.login(username='bob', password='password123')

        # List
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 404)

        # Create
        response = self.client.post(self.create_url, data={'name': 'Jane'})
        self.assertEqual(response.status_code, 404)

        # Update
        response = self.client.post(self.update_url, data={'name': 'Jane'})
        self.assertEqual(response.status_code, 404)

        # Delete
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 404)

    def test_member_list_success(self):
        """Verify creator can view member list."""
        self.client.login(username='alice', password='password123')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/member_list.html')
        self.assertContains(response, 'John Doe')

    def test_member_create_success(self):
        """Verify creator can add a member to the group."""
        self.client.login(username='alice', password='password123')
        payload = {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'phone': '9876543210'
        }
        response = self.client.post(self.create_url, data=payload)
        self.assertRedirects(response, self.list_url)
        self.assertTrue(Member.objects.filter(name='Jane Smith', group=self.group).exists())

    def test_member_create_duplicate_validation(self):
        """Verify duplicate member names within the same group are prevented."""
        self.client.login(username='alice', password='password123')
        payload = {
            'name': 'John Doe',  # Case-insensitive duplicate check
            'email': 'john2@example.com',
        }
        response = self.client.post(self.create_url, data=payload)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn("A member with this name already exists in this group.", form.errors['name'][0])

    def test_member_update_success(self):
        """Verify creator can update member details."""
        self.client.login(username='alice', password='password123')
        payload = {
            'name': 'John Updated',
            'email': 'updated@example.com',
            'phone': '1112223333'
        }
        response = self.client.post(self.update_url, data=payload)
        self.assertRedirects(response, self.list_url)
        self.member.refresh_from_db()
        self.assertEqual(self.member.name, 'John Updated')
        self.assertEqual(self.member.email, 'updated@example.com')

    def test_member_delete_success(self):
        """Verify creator can remove a member."""
        self.client.login(username='alice', password='password123')
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, self.list_url)
        self.assertFalse(Member.objects.filter(pk=self.member.pk).exists())


class ExpenseCRUDTests(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='alice', email='alice@example.com', password='password123')
        self.user2 = User.objects.create_user(username='bob', email='bob@example.com', password='password123')

        # Create Alice's Group
        self.group = Group.objects.create(
            name='Alice Goa Trip',
            description='Trip to Goa funded by Alice',
            created_by=self.user1
        )
        self.group.members.add(self.user1)

        # Create members for Alice's Group
        self.member1 = Member.objects.create(group=self.group, name='John Doe', email='john@example.com')
        self.member2 = Member.objects.create(group=self.group, name='Jane Doe', email='jane@example.com')

        # Create a group for Bob to verify separation
        self.bob_group = Group.objects.create(
            name='Bob Secret Group',
            created_by=self.user2
        )
        self.bob_member = Member.objects.create(group=self.bob_group, name='Charlie')

        # Create an expense in Alice's Group
        self.expense = Expense.objects.create(
            group=self.group,
            title='Dinner at beach',
            amount=1500.00,
            paid_by=self.member1,
            date=date.today(),
            category='Food',
            created_by=self.user1
        )

        # URLs for Alice's Group
        self.list_url = reverse('expense_list', args=[self.group.pk])
        self.create_url = reverse('expense_create', args=[self.group.pk])
        self.detail_url = reverse('expense_detail', args=[self.group.pk, self.expense.pk])
        self.update_url = reverse('expense_update', args=[self.group.pk, self.expense.pk])
        self.delete_url = reverse('expense_delete', args=[self.group.pk, self.expense.pk])
        
        self.login_url = reverse('login')

    def test_expense_pages_require_login(self):
        """Verify unauthenticated users cannot access expense pages."""
        urls = [self.list_url, self.create_url, self.detail_url, self.update_url, self.delete_url]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"{self.login_url}?next={url}")

    def test_expense_pages_unauthorized(self):
        """Verify logged-in user cannot manage expenses in a group they don't own."""
        self.client.login(username='bob', password='password123')
        urls = [self.list_url, self.create_url, self.detail_url, self.update_url, self.delete_url]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)

            # Test POST queries too
            if url == self.create_url:
                response = self.client.post(url, data={'title': 'Steal'})
            elif url == self.delete_url:
                response = self.client.post(url)
            else:
                response = self.client.post(url, data={'title': 'Steal'})
            self.assertEqual(response.status_code, 404)

    def test_expense_list_success(self):
        """Verify creator can view expense list and sum total."""
        self.client.login(username='alice', password='password123')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/expense_list.html')
        self.assertContains(response, 'Dinner at beach')
        self.assertEqual(response.context['total_amount'], 1500.00)

    def test_expense_detail_success(self):
        """Verify creator can view expense detail page."""
        self.client.login(username='alice', password='password123')
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/expense_detail.html')
        self.assertContains(response, 'Dinner at beach')
        self.assertContains(response, 'Food')

    def test_expense_create_success(self):
        """Verify creator can add a new expense."""
        self.client.login(username='alice', password='password123')
        payload = {
            'title': 'Cab Fare',
            'description': 'Goa Airport to hotel',
            'amount': 1200.00,
            'paid_by': self.member2.pk,
            'date': date.today(),
            'category': 'Travel',
            'notes': 'Paid in cash'
        }
        response = self.client.post(self.create_url, data=payload)
        self.assertRedirects(response, self.list_url)
        self.assertTrue(Expense.objects.filter(title='Cab Fare', group=self.group).exists())

    def test_expense_create_invalid_amount(self):
        """Verify validation errors if expense amount is 0 or negative."""
        self.client.login(username='alice', password='password123')
        payload = {
            'title': 'Free Water',
            'amount': 0.00,  # invalid amount
            'paid_by': self.member1.pk,
            'date': date.today(),
            'category': 'Drinks'
        }
        response = self.client.post(self.create_url, data=payload)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        self.assertIn("Expense amount must be greater than zero.", form.errors['amount'][0])

    def test_expense_paid_by_dropdown_filtering(self):
        """Verify that only members of the current group are available in paid_by dropdown."""
        self.client.login(username='alice', password='password123')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        
        # Check that member1 and member2 are present in paid_by choices, but bob_member is not
        form = response.context['form']
        queryset = form.fields['paid_by'].queryset
        self.assertIn(self.member1, queryset)
        self.assertIn(self.member2, queryset)
        self.assertNotIn(self.bob_member, queryset)

    def test_expense_update_success(self):
        """Verify creator can update expense details."""
        self.client.login(username='alice', password='password123')
        payload = {
            'title': 'Dinner at beach (Updated)',
            'description': 'Description change',
            'amount': 1800.00,
            'paid_by': self.member1.pk,
            'date': date.today(),
            'category': 'Food'
        }
        response = self.client.post(self.update_url, data=payload)
        self.assertRedirects(response, self.list_url)
        
        self.expense.refresh_from_db()
        self.assertEqual(self.expense.title, 'Dinner at beach (Updated)')
        self.assertEqual(self.expense.amount, 1800.00)

    def test_expense_delete_success(self):
        """Verify creator can delete expense."""
        self.client.login(username='alice', password='password123')
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, self.list_url)
        self.assertFalse(Expense.objects.filter(pk=self.expense.pk).exists())



