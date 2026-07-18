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

        # Create members for paid_by checks and splits
        self.member1 = Member.objects.create(
            group=self.group,
            name='Alice Member',
            email='alice@example.com'
        )
        self.member2 = Member.objects.create(
            group=self.group,
            name='Bob Member',
            email='bob@example.com'
        )
        self.member3 = Member.objects.create(
            group=self.group,
            name='Charlie Member',
            email='charlie@example.com'
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
        split1 = ExpenseSplit.objects.create(expense=expense, member=self.member1, amount=30.00)
        split2 = ExpenseSplit.objects.create(expense=expense, member=self.member2, amount=30.00)
        split3 = ExpenseSplit.objects.create(expense=expense, member=self.member3, amount=30.00)

        self.assertEqual(expense.splits.count(), 3)
        self.assertEqual(split1.amount, 30.00)
        self.assertEqual(str(split1), "Alice Member owes 30.00 for Dinner bill")

        # Test unique_together constraint on (expense, member)
        with self.assertRaises(IntegrityError):
            ExpenseSplit.objects.create(expense=expense, member=self.member1, amount=10.00)

    def test_settlement(self):
        settlement = Settlement.objects.create(
            group=self.group,
            payer=self.member2,
            payee=self.member1,
            amount=30.00,
            status='completed'
        )
        self.assertEqual(settlement.payer, self.member2)
        self.assertEqual(settlement.payee, self.member1)
        self.assertEqual(settlement.amount, 30.00)
        self.assertEqual(settlement.status, 'completed')
        self.assertEqual(str(settlement), "Bob Member paid Alice Member 30.00 in Trip to Goa")

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


class ExpenseSplitTests(TestCase):
    def setUp(self):
        # Create test users
        self.owner = User.objects.create_user(username='owner', email='owner@example.com', password='password123')
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password123')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='password123')
        self.other_user = User.objects.create_user(username='other', email='other@example.com', password='password123')

        # Create group and add owner, user1, user2 to members
        self.group = Group.objects.create(name='Goa Trip', description='Fun trip', created_by=self.owner)
        self.group.members.add(self.owner, self.user1, self.user2)

        # Create group members (fetched from selected group's Member model)
        self.member_owner = Member.objects.create(group=self.group, name='Owner Member', email='owner@example.com')
        self.member_user1 = Member.objects.create(group=self.group, name='User1 Member', email='user1@example.com')
        self.member_user2 = Member.objects.create(group=self.group, name='User2 Member', email='user2@example.com')

        # Create expense
        self.expense = Expense.objects.create(
            group=self.group,
            title='Beach Dinner',
            amount=100.00,
            paid_by=self.member_owner,
            date=date.today(),
            category='Food',
            created_by=self.owner
        )

        # URLs
        self.split_url = reverse('expense_split', kwargs={'group_pk': self.group.pk, 'expense_pk': self.expense.pk})
        self.equal_preview_url = reverse('equal_split_preview', kwargs={'group_pk': self.group.pk, 'expense_pk': self.expense.pk})
        self.unequal_form_url = reverse('unequal_split_form', kwargs={'group_pk': self.group.pk, 'expense_pk': self.expense.pk})
        self.result_url = reverse('split_result', kwargs={'group_pk': self.group.pk, 'expense_pk': self.expense.pk})

    def test_expense_split_requires_authentication(self):
        """Verify only logged in users can view the split setup page."""
        response = self.client.get(self.split_url)
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_expense_split_restricted_to_group_creator(self):
        """Verify other users cannot access split pages for groups they don't own."""
        self.client.login(username='other', password='password123')
        response = self.client.get(self.split_url)
        self.assertEqual(response.status_code, 404)  # Restricted

    def test_split_setup_view_loads_members(self):
        """Verify the setup page displays all group members with checkboxes."""
        self.client.login(username='owner', password='password123')
        response = self.client.get(self.split_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Owner Member')
        self.assertContains(response, 'User1 Member')
        self.assertContains(response, 'User2 Member')

    def test_split_setup_post_validation(self):
        """Verify selecting no members throws an error."""
        self.client.login(username='owner', password='password123')
        payload = {
            'selected_members': [],
            'split_method': 'equal'
        }
        response = self.client.post(self.split_url, data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please select at least one member to split.")

    def test_equal_split_preview_calculation_and_rounding(self):
        """Verify equal split correctly rounds and distributes remainder cents."""
        self.client.login(username='owner', password='password123')
        
        # Select all 3 members (100.00 / 3 = 33.33 with 0.01 remainder)
        payload = {
            'selected_members': [self.member_owner.id, self.member_user1.id, self.member_user2.id],
            'split_method': 'equal'
        }
        response = self.client.post(self.split_url, data=payload)
        self.assertRedirects(response, self.equal_preview_url)

        # Get preview page
        preview_response = self.client.get(self.equal_preview_url)
        self.assertEqual(preview_response.status_code, 200)
        
        # Check calculated preview shares in context
        splits_preview = preview_response.context['splits']
        self.assertEqual(len(splits_preview), 3)
        
        # Rounding logic test: One member should get 33.34, others 33.33
        amounts = [float(item['amount']) for item in splits_preview]
        self.assertIn(33.34, amounts)
        self.assertEqual(amounts.count(33.33), 2)
        self.assertEqual(sum(amounts), 100.00)

        # Confirm splits save
        confirm_response = self.client.post(self.equal_preview_url)
        self.assertRedirects(confirm_response, self.result_url)

        # Verify splits saved in DB
        db_splits = ExpenseSplit.objects.filter(expense=self.expense)
        self.assertEqual(db_splits.count(), 3)
        self.assertEqual(sum(float(s.amount) for s in db_splits), 100.00)

    def test_unequal_split_validation_and_saving(self):
        """Verify custom split amount inputs are validated properly."""
        self.client.login(username='owner', password='password123')
        
        # Go to setup page and select owner and user1 members
        payload = {
            'selected_members': [self.member_owner.id, self.member_user1.id],
            'split_method': 'unequal'
        }
        response = self.client.post(self.split_url, data=payload)
        self.assertRedirects(response, self.unequal_form_url)

        # 1. Invalid unequal split (amounts do not sum to total expense)
        post_payload = {
            f'amount_{self.member_owner.id}': '40.00',
            f'amount_{self.member_user1.id}': '50.00',  # Sums to 90, expected 100
        }
        err_response = self.client.post(self.unequal_form_url, data=post_payload)
        self.assertEqual(err_response.status_code, 200)
        self.assertContains(err_response, "must exactly equal the total expense amount")

        # 2. Invalid unequal split (negative value)
        post_payload = {
            f'amount_{self.member_owner.id}': '-10.00',
            f'amount_{self.member_user1.id}': '110.00',
        }
        err_response = self.client.post(self.unequal_form_url, data=post_payload)
        self.assertEqual(err_response.status_code, 200)
        self.assertContains(err_response, "Split amounts cannot be negative.")

        # 3. Valid unequal split (sums to 100)
        post_payload = {
            f'amount_{self.member_owner.id}': '35.50',
            f'amount_{self.member_user1.id}': '64.50',
        }
        success_response = self.client.post(self.unequal_form_url, data=post_payload)
        self.assertRedirects(success_response, self.result_url)

        # Verify splits saved: selected members get values, unselected get 0.00
        db_splits = ExpenseSplit.objects.filter(expense=self.expense)
        self.assertEqual(db_splits.count(), 3)  # Owner, user1, and user2 members
        
        owner_split = db_splits.get(member=self.member_owner)
        user1_split = db_splits.get(member=self.member_user1)
        user2_split = db_splits.get(member=self.member_user2)

        self.assertEqual(float(owner_split.amount), 35.50)
        self.assertEqual(float(user1_split.amount), 64.50)
        self.assertEqual(float(user2_split.amount), 0.00)

    def test_recalculate_splits_deletes_old_records(self):
        """Verify that running split again overwrites any existing split records."""
        self.client.login(username='owner', password='password123')
        
        # Save first split (Equal Split: owner = 50.00, user1 = 50.00, user2 = 0.00)
        ExpenseSplit.objects.create(expense=self.expense, member=self.member_owner, amount=50.00)
        ExpenseSplit.objects.create(expense=self.expense, member=self.member_user1, amount=50.00)
        ExpenseSplit.objects.create(expense=self.expense, member=self.member_user2, amount=0.00)

        self.assertEqual(ExpenseSplit.objects.filter(expense=self.expense).count(), 3)

        # Run Equal Split again with all 3 members (distributes 100.00 among 3)
        self.client.post(self.split_url, data={
            'selected_members': [self.member_owner.id, self.member_user1.id, self.member_user2.id],
            'split_method': 'equal'
        })
        self.client.post(self.equal_preview_url)

        # Verify old 50.00 records are gone and replaced by the rounded equal division
        db_splits = ExpenseSplit.objects.filter(expense=self.expense)
        self.assertEqual(db_splits.count(), 3)
        amounts = [float(s.amount) for s in db_splits]
        self.assertNotIn(50.00, amounts)
        self.assertIn(33.34, amounts)
        self.assertEqual(sum(amounts), 100.00)


class SettlementAndBalanceTests(TestCase):
    def setUp(self):
        # Create user and group
        self.owner = User.objects.create_user(username='owner', password='password123')
        self.other_user = User.objects.create_user(username='other', password='password123')
        
        self.group = Group.objects.create(name='Trip Group', created_by=self.owner)
        self.group.members.add(self.owner)
        
        # Create members
        self.member_raj = Member.objects.create(group=self.group, name='Raj')
        self.member_netra = Member.objects.create(group=self.group, name='Netra')
        self.member_rohan = Member.objects.create(group=self.group, name='Rohan')

    def test_recalculate_group_settlements_correctness(self):
        from decimal import Decimal
        # Expense: 3000 paid by Raj, split equally between Raj, Netra, Rohan (1000 each)
        expense = Expense.objects.create(
            group=self.group,
            title='Dinner',
            amount=Decimal('3000.00'),
            paid_by=self.member_raj,
            date='2026-07-05',
            category='Food',
            created_by=self.owner
        )
        ExpenseSplit.objects.create(expense=expense, member=self.member_raj, amount=Decimal('1000.00'))
        ExpenseSplit.objects.create(expense=expense, member=self.member_netra, amount=Decimal('1000.00'))
        ExpenseSplit.objects.create(expense=expense, member=self.member_rohan, amount=Decimal('1000.00'))
        
        # Recalculate
        from .views import recalculate_group_settlements
        balances = recalculate_group_settlements(self.group)
        
        # Verify balances
        raj_bal = next(b for b in balances if b['member'].id == self.member_raj.id)
        netra_bal = next(b for b in balances if b['member'].id == self.member_netra.id)
        rohan_bal = next(b for b in balances if b['member'].id == self.member_rohan.id)
        
        self.assertEqual(raj_bal['net_balance'], Decimal('2000.00'))
        self.assertEqual(netra_bal['net_balance'], Decimal('-1000.00'))
        self.assertEqual(rohan_bal['net_balance'], Decimal('-1000.00'))
        
        # Verify pending settlements auto-created
        pending = Settlement.objects.filter(group=self.group, status='pending')
        self.assertEqual(pending.count(), 2)
        
        # Settle Netra's debt: mark the settlement as completed
        settlement = pending.filter(payer=self.member_netra).first()
        settlement.status = 'completed'
        settlement.save()
        
        # Recalculate again
        balances = recalculate_group_settlements(self.group)
        raj_bal = next(b for b in balances if b['member'].id == self.member_raj.id)
        netra_bal = next(b for b in balances if b['member'].id == self.member_netra.id)
        rohan_bal = next(b for b in balances if b['member'].id == self.member_rohan.id)
        
        # Netra should now have 0 net balance
        self.assertEqual(netra_bal['net_balance'], Decimal('0.00'))
        # Raj should have 1000 left to receive
        self.assertEqual(raj_bal['net_balance'], Decimal('1000.00'))
        # Rohan still owes 1000
        self.assertEqual(rohan_bal['net_balance'], Decimal('-1000.00'))
        
        # Verify only 1 pending settlement left (Rohan owes Raj 1000)
        remaining_pending = Settlement.objects.filter(group=self.group, status='pending')
        self.assertEqual(remaining_pending.count(), 1)
        self.assertEqual(remaining_pending.first().payer, self.member_rohan)
        self.assertEqual(remaining_pending.first().payee, self.member_raj)
        self.assertEqual(remaining_pending.first().amount, Decimal('1000.00'))

    def test_settlement_form_validation(self):
        from .forms import SettlementForm
        from decimal import Decimal
        
        # 1. Invalid amount <= 0
        form = SettlementForm(data={
            'payer': self.member_netra.id,
            'payee': self.member_raj.id,
            'amount': '0.00',
            'status': 'pending'
        }, group=self.group)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        
        # 2. Same payer and payee
        form = SettlementForm(data={
            'payer': self.member_raj.id,
            'payee': self.member_raj.id,
            'amount': '500.00',
            'status': 'pending'
        }, group=self.group)
        self.assertFalse(form.is_valid())
        self.assertIn('payee', form.errors)

        # 3. Duplicate check
        Settlement.objects.create(
            group=self.group,
            payer=self.member_netra,
            payee=self.member_raj,
            amount=Decimal('500.00'),
            status='completed'
        )
        form = SettlementForm(data={
            'payer': self.member_netra.id,
            'payee': self.member_raj.id,
            'amount': '500.00',
            'status': 'completed'
        }, group=self.group)
        self.assertFalse(form.is_valid())

    def test_views_access_controls(self):
        from decimal import Decimal
        # Create a pending settlement
        settlement = Settlement.objects.create(
            group=self.group,
            payer=self.member_netra,
            payee=self.member_raj,
            amount=Decimal('1000.00'),
            status='pending'
        )
        
        # 1. Unauthenticated users are blocked
        response = self.client.get(reverse('balance_dashboard', args=[self.group.id]))
        self.assertEqual(response.status_code, 302)  # redirects to login
        
        # 2. Non-owners are blocked
        self.client.login(username='other', password='password123')
        response = self.client.get(reverse('balance_dashboard', args=[self.group.id]))
        self.assertEqual(response.status_code, 404)
        
        # 3. Creator can access
        self.client.login(username='owner', password='password123')
        response = self.client.get(reverse('balance_dashboard', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Raj')
        
        # 4. Completed settlement cannot be re-completed
        settlement.status = 'completed'
        settlement.save()
        confirm_url = reverse('settlement_confirm', args=[self.group.id, settlement.id])
        response = self.client.get(confirm_url)
        # Should redirect to detail page with warning message
        self.assertEqual(response.status_code, 302)




