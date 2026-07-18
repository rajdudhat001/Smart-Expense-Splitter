from django.contrib import admin
from .models import Group, Expense, ExpenseSplit, Settlement, Budget, Member, Invitation

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('members',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'group', 'paid_by', 'date')
    list_filter = ('group', 'date')
    search_fields = ('description',)

@admin.register(ExpenseSplit)
class ExpenseSplitAdmin(admin.ModelAdmin):
    list_display = ('expense', 'member', 'amount', 'is_settled')
    list_filter = ('is_settled',)
    search_fields = ('member__name', 'expense__description')

@admin.register(Settlement)
class SettlementAdmin(admin.ModelAdmin):
    list_display = ('group', 'payer', 'payee', 'amount', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('payer__username', 'payee__username')

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'amount_limit', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('group__name', 'user__username')

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'user', 'email', 'created_at')
    search_fields = ('name', 'email')

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('group', 'email', 'invited_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('email', 'group__name')


