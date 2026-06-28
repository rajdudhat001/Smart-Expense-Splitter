from django.contrib import admin
from .models import Group, Expense, ExpenseSplit, Settlement, Budget

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
    list_display = ('expense', 'user', 'amount', 'is_settled')
    list_filter = ('is_settled',)
    search_fields = ('user__username', 'expense__description')

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


