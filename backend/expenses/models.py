from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='expense_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='expenses_paid')
    date = models.DateField()
    category = models.CharField(max_length=50)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.amount:.2f} in {self.group.name}"

class ExpenseSplit(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    member = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='splits_owed')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_settled = models.BooleanField(default=False)

    class Meta:
        unique_together = ('expense', 'member')

    def __str__(self):
        return f"{self.member.name} owes {self.amount:.2f} for {self.expense.title}"


class Settlement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='settlements')
    payer = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='settlements_sent')
    payee = models.ForeignKey('Member', on_delete=models.CASCADE, related_name='settlements_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.payer.name} paid {self.payee.name} {self.amount:.2f} in {self.group.name}"

class Budget(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='budgets', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets', null=True, blank=True)
    amount_limit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.group:
            return f"Budget of {self.amount_limit:.2f} for group {self.group.name}"
        return f"Personal budget of {self.amount_limit:.2f} for {self.user.username}"


class Member(models.Model):
    """
    Model representing a member of a group.
    Each member belongs to exactly one group.
    """
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_members')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='group_memberships')
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'name')

    def __str__(self):
        return f"{self.name} in {self.group.name}"


class Invitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'email')

    def __str__(self):
        return f"Invite for {self.email} to {self.group.name}"




