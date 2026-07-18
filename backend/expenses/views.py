from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserLoginForm, GroupForm, MemberForm, ExpenseForm, SettlementForm
from .models import Group, Member, Expense, ExpenseSplit, Settlement
from decimal import Decimal, ROUND_DOWN
from django.db import models

def register_view(request):
    """
    View for registering new users.
    """
    # If the user is already logged in, redirect them to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        # Bind request POST data to the registration form
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save the new user and redirect to the login page
            form.save()
            return redirect('login')
    else:
        # Provide an empty registration form
        form = UserRegistrationForm()
        
    return render(request, 'expenses/register.html', {'form': form})


def login_view(request):
    """
    View for logging in existing users.
    """
    # If the user is already logged in, redirect them to the dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_message = None
    if request.method == 'POST':
        # Bind request POST data to the login form
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Authenticate the user checking credentials against the database
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Log the authenticated user into the session
                login(request, user)
                return redirect('dashboard')
            else:
                # Set an error message if authentication fails
                error_message = "Invalid username or password."
    else:
        # Provide an empty login form
        form = UserLoginForm()
        
    return render(request, 'expenses/login.html', {'form': form, 'error_message': error_message})


def logout_view(request):
    """
    View to log out the current user and redirect to login page.
    """
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard_view(request):
    """
    A protected view representing the dashboard, only accessible if logged in.
    """
    return render(request, 'expenses/dashboard.html', {'user': request.user})


@login_required(login_url='login')
def group_list_view(request):
    """
    View to display all groups created by the authenticated user.
    """
    groups = Group.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'expenses/group_list.html', {'groups': groups})


@login_required(login_url='login')
def group_create_view(request):
    """
    View to create a new group.
    """
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            # Automatically add the creator as a member of the group
            group.members.add(request.user)
            messages.success(request, "Group created successfully!")
            return redirect('group_list')
        else:
            messages.error(request, "Error creating group. Please fix the errors below.")
    else:
        form = GroupForm()
    return render(request, 'expenses/group_create.html', {'form': form})


@login_required(login_url='login')
def group_update_view(request, pk):
    """
    View to edit/update an existing group. Access is restricted to the group creator.
    """
    group = get_object_or_404(Group, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Group updated successfully!")
            return redirect('group_list')
        else:
            messages.error(request, "Error updating group. Please fix the errors below.")
    else:
        form = GroupForm(instance=group)
    return render(request, 'expenses/group_update.html', {'form': form, 'group': group})


@login_required(login_url='login')
def group_delete_view(request, pk):
    """
    View to delete an existing group. Access is restricted to the group creator.
    """
    group = get_object_or_404(Group, pk=pk, created_by=request.user)
    if request.method == 'POST':
        group.delete()
        messages.success(request, "Group deleted successfully!")
        return redirect('group_list')
    return render(request, 'expenses/group_delete.html', {'group': group})


@login_required(login_url='login')
def member_list_view(request, group_pk):
    """
    View members of a group. Access restricted to group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    members = group.group_members.all().order_by('name')
    return render(request, 'expenses/member_list.html', {'group': group, 'members': members})


@login_required(login_url='login')
def member_create_view(request, group_pk):
    """
    Add a new member to a group. Access restricted to group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    if request.method == 'POST':
        form = MemberForm(request.POST, group=group)
        if form.is_valid():
            member = form.save(commit=False)
            member.group = group
            member.save()
            messages.success(request, "Member added successfully!")
            return redirect('member_list', group_pk=group.pk)
        else:
            messages.error(request, "Error adding member. Please fix the errors below.")
    else:
        form = MemberForm(group=group)
    return render(request, 'expenses/member_create.html', {'form': form, 'group': group})


@login_required(login_url='login')
def member_update_view(request, group_pk, member_pk):
    """
    Update member details. Access restricted to group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    member = get_object_or_404(Member, pk=member_pk, group=group)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member, group=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Member updated successfully!")
            return redirect('member_list', group_pk=group.pk)
        else:
            messages.error(request, "Error updating member. Please fix the errors below.")
    else:
        form = MemberForm(instance=member, group=group)
    return render(request, 'expenses/member_update.html', {'form': form, 'group': group, 'member': member})


@login_required(login_url='login')
def member_delete_view(request, group_pk, member_pk):
    """
    Remove member from group. Access restricted to group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    member = get_object_or_404(Member, pk=member_pk, group=group)
    if request.method == 'POST':
        member_name = member.name
        member.delete()
        messages.success(request, f"Member '{member_name}' removed successfully!")
        return redirect('member_list', group_pk=group.pk)
    return render(request, 'expenses/member_delete.html', {'group': group, 'member': member})


@login_required(login_url='login')
def expense_list_view(request, group_pk):
    """
    List all expenses inside a group. Access restricted to group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    expenses = group.expenses.all().order_by('-date', '-created_at')
    
    # Calculate sum total of expenses in the group
    total_amount = sum(expense.amount for expense in expenses)
    return render(request, 'expenses/expense_list.html', {
        'group': group,
        'expenses': expenses,
        'total_amount': total_amount
    })


@login_required(login_url='login')
def expense_detail_view(request, group_pk, expense_pk):
    """
    Display details of a specific expense. Access restricted to group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    expense = get_object_or_404(Expense, pk=expense_pk, group=group)
    return render(request, 'expenses/expense_detail.html', {
        'group': group,
        'expense': expense
    })


@login_required(login_url='login')
def expense_create_view(request, group_pk):
    """
    Add a new expense. Access restricted to group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    
    # Verify the group has at least one member to attribute "Paid By"
    if not group.group_members.exists():
        messages.error(request, "Please add at least one member to the group before adding expenses.")
        return redirect('member_list', group_pk=group.pk)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, group=group)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            expense.created_by = request.user
            expense.save()
            messages.success(request, "Expense added successfully!")
            return redirect('expense_list', group_pk=group.pk)
        else:
            messages.error(request, "Error adding expense. Please fix the errors below.")
    else:
        form = ExpenseForm(group=group)
    return render(request, 'expenses/expense_create.html', {
        'form': form,
        'group': group
    })


@login_required(login_url='login')
def expense_update_view(request, group_pk, expense_pk):
    """
    Update details of an existing expense. Access restricted to group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    expense = get_object_or_404(Expense, pk=expense_pk, group=group)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, group=group)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense updated successfully!")
            return redirect('expense_list', group_pk=group.pk)
        else:
            messages.error(request, "Error updating expense. Please fix the errors below.")
    else:
        form = ExpenseForm(instance=expense, group=group)
    return render(request, 'expenses/expense_update.html', {
        'form': form,
        'group': group,
        'expense': expense
    })


@login_required(login_url='login')
def expense_delete_view(request, group_pk, expense_pk):
    """
    Delete an existing expense. Access restricted to group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    expense = get_object_or_404(Expense, pk=expense_pk, group=group)
    
    if request.method == 'POST':
        expense_title = expense.title
        expense.delete()
        messages.success(request, f"Expense '{expense_title}' deleted successfully!")
        return redirect('expense_list', group_pk=group.pk)
    return render(request, 'expenses/expense_delete.html', {
        'group': group,
        'expense': expense
    })


@login_required(login_url='login')
def expense_split_view(request, group_pk, expense_pk):
    """
    View to start the split process for an expense.
    Allows selecting group members and choose between equal or unequal split method.
    """
    # Verify group ownership and retrieve objects
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    expense = get_object_or_404(Expense, pk=expense_pk, group=group)
    
    # Retrieve all Members who are part of this group
    group_members = group.group_members.all().order_by('name')
    
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_members')
        split_method = request.POST.get('split_method')
        
        # Validation: Ensure at least one member is selected
        if not selected_ids:
            messages.error(request, "Please select at least one member to split.")
            return render(request, 'expenses/expense_split.html', {
                'group': group,
                'expense': expense,
                'group_members': group_members
            })
            
        # Parse member IDs to integer values
        try:
            selected_ids = [int(x) for x in selected_ids]
        except ValueError:
            messages.error(request, "Invalid input received.")
            return redirect('expense_split', group_pk=group_pk, expense_pk=expense_pk)
            
        # Security validation: Ensure selected members actually belong to the group
        valid_members_count = group.group_members.filter(id__in=selected_ids).count()
        if valid_members_count != len(selected_ids):
            messages.error(request, "Some selected members do not belong to this group.")
            return redirect('expense_split', group_pk=group_pk, expense_pk=expense_pk)
            
        # Store selected members and method in the user session
        request.session['split_member_ids'] = selected_ids
        request.session['split_method'] = split_method
        
        # Redirect to the chosen split method view
        if split_method == 'equal':
            return redirect('equal_split_preview', group_pk=group_pk, expense_pk=expense_pk)
        elif split_method == 'unequal':
            return redirect('unequal_split_form', group_pk=group_pk, expense_pk=expense_pk)
        else:
            messages.error(request, "Invalid split method.")
            
    return render(request, 'expenses/expense_split.html', {
        'group': group,
        'expense': expense,
        'group_members': group_members
    })


@login_required(login_url='login')
def equal_split_preview_view(request, group_pk, expense_pk):
    """
    View to preview equal split calculations before confirming and saving to DB.
    Handles division rounding cents by allocating them to the first members.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    expense = get_object_or_404(Expense, pk=expense_pk, group=group)
    
    # Retrieve splitting data from user session
    selected_ids = request.session.get('split_member_ids', [])
    split_method = request.session.get('split_method', 'equal')
    
    # Validation: Ensure they initiated the split page first
    if not selected_ids or split_method != 'equal':
        messages.error(request, "Please select members first.")
        return redirect('expense_split', group_pk=group_pk, expense_pk=expense_pk)
        
    selected_members = list(Member.objects.filter(id__in=selected_ids).order_by('name'))
    
    # Security validation: Ensure all session members belong to this group
    if not all(m.group == group for m in selected_members):
        messages.error(request, "Invalid session members.")
        return redirect('expense_split', group_pk=group_pk, expense_pk=expense_pk)
        
    total_amount = Decimal(str(expense.amount))
    n = len(selected_members)
    
    # Equal split rounding algorithm:
    # Divide total amount by number of members, round down to 2 decimal places.
    # Distribute the remainder cents (if any) to the first few members.
    base_share = (total_amount / n).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    total_splits = base_share * n
    remainder = total_amount - total_splits
    remainder_cents = int(remainder * 100)
    
    splits_preview = []
    for i, m in enumerate(selected_members):
        amount = base_share
        if i < remainder_cents:
            amount += Decimal('0.01')
        splits_preview.append({
            'member': m,
            'amount': amount
        })
        
    if request.method == 'POST':
        # 1. Delete any existing splits for this expense (allows recalculations/resplits)
        ExpenseSplit.objects.filter(expense=expense).delete()
        
        # 2. Save new splits: selected members get their calculated share, unselected get 0.00
        all_group_members = group.group_members.all()
        for m in all_group_members:
            share_amount = Decimal('0.00')
            for preview in splits_preview:
                if preview['member'].id == m.id:
                    share_amount = preview['amount']
                    break
            
            ExpenseSplit.objects.create(
                expense=expense,
                member=m,
                amount=share_amount
            )
            
        messages.success(request, "Equal split saved successfully!")
        return redirect('split_result', group_pk=group_pk, expense_pk=expense_pk)
        
    return render(request, 'expenses/equal_split_preview.html', {
        'group': group,
        'expense': expense,
        'splits': splits_preview
    })


@login_required(login_url='login')
def unequal_split_form_view(request, group_pk, expense_pk):
    """
    View for entering custom split amounts manually for each selected group member.
    Validates that total entered matches expense amount exactly, and values are non-negative.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    expense = get_object_or_404(Expense, pk=expense_pk, group=group)
    
    # Retrieve splitting data from user session
    selected_ids = request.session.get('split_member_ids', [])
    split_method = request.session.get('split_method', 'unequal')
    
    # Validation: Ensure they initiated the split page first
    if not selected_ids or split_method != 'unequal':
        messages.error(request, "Please select members first.")
        return redirect('expense_split', group_pk=group_pk, expense_pk=expense_pk)
        
    selected_members = list(Member.objects.filter(id__in=selected_ids).order_by('name'))
    
    # Security validation: Ensure all session members belong to this group
    if not all(m.group == group for m in selected_members):
        messages.error(request, "Invalid session members.")
        return redirect('expense_split', group_pk=group_pk, expense_pk=expense_pk)
        
    total_expense = Decimal(str(expense.amount))
    error_message = None
    previous_values = {}
    
    if request.method == 'POST':
        total_entered = Decimal('0.00')
        valid = True
        entered_shares = {}
        
        for m in selected_members:
            val_str = request.POST.get(f'amount_{m.id}', '0.00').strip()
            try:
                val = Decimal(val_str)
                # Validation rules:
                if val < 0:
                    error_message = "Split amounts cannot be negative."
                    valid = False
                elif val > total_expense:
                    error_message = "Split amount cannot exceed total expense."
                    valid = False
                else:
                    entered_shares[m.id] = val
                    total_entered += val
                    previous_values[m.id] = val
            except (ValueError, TypeError):
                error_message = "Invalid number entered."
                valid = False
                previous_values[m.id] = Decimal('0.00')
                
        if valid:
            # Validation rule: check if sum of entered shares exactly matches total expense amount
            diff = abs(total_expense - total_entered)
            if diff >= Decimal('0.01'):
                error_message = f"The total split amounts (₹{total_entered:.2f}) must exactly equal the total expense amount (₹{total_expense:.2f}). Difference is ₹{(total_expense - total_entered):.2f}."
                valid = False
                
        if valid:
            # 1. Delete any existing splits for this expense
            ExpenseSplit.objects.filter(expense=expense).delete()
            
            # 2. Save splits: selected members get their entered custom amounts, others get 0.00
            all_group_members = group.group_members.all()
            for m in all_group_members:
                share_amount = entered_shares.get(m.id, Decimal('0.00'))
                ExpenseSplit.objects.create(
                    expense=expense,
                    member=m,
                    amount=share_amount
                )
                
            messages.success(request, "Unequal split saved successfully!")
            return redirect('split_result', group_pk=group_pk, expense_pk=expense_pk)
            
    # Prepare previous values or default values to avoid template rendering issues
    members_with_amounts = []
    for m in selected_members:
        members_with_amounts.append({
            'member': m,
            'amount': previous_values.get(m.id, Decimal('0.00'))
        })
        
    return render(request, 'expenses/unequal_split_form.html', {
        'group': group,
        'expense': expense,
        'members_with_amounts': members_with_amounts,
        'error_message': error_message
    })


@login_required(login_url='login')
def split_result_view(request, group_pk, expense_pk):
    """
    View to display the saved split results for a specific expense.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    expense = get_object_or_404(Expense, pk=expense_pk, group=group)
    splits = expense.splits.all().order_by('member__name')
    return render(request, 'expenses/split_result.html', {
        'group': group,
        'expense': expense,
        'splits': splits
    })


def recalculate_group_settlements(group):
    """
    Helper function to calculate member balances and automatically generate/sync
    pending Settlements based on the greedy debt simplification algorithm.
    """
    members = list(group.group_members.all())
    if not members:
        # If there are no members, clear all pending settlements
        group.settlements.filter(status='pending').delete()
        return []

    balances = {}
    for m in members:
        # Total paid as the payer of expenses in the group
        total_paid = Expense.objects.filter(group=group, paid_by=m).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        # Total owed as a participant of expenses splits in the group
        total_owes = ExpenseSplit.objects.filter(expense__group=group, member=m).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        # Total completed settlements sent by this member as payer
        settlements_sent = Settlement.objects.filter(group=group, payer=m, status='completed').aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        # Total completed settlements received by this member as payee
        settlements_received = Settlement.objects.filter(group=group, payee=m, status='completed').aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        # Net balance calculation: (Paid + Sent) - (Owed + Received)
        net_balance = (total_paid + settlements_sent) - (total_owes + settlements_received)
        
        # Total receivable is Net Balance if positive, else zero
        receivable = net_balance if net_balance > 0 else Decimal('0.00')
        
        balances[m.id] = {
            'member': m,
            'paid': total_paid,
            'owes': total_owes,
            'receivable': receivable,
            'net_balance': net_balance,
            'net_balance_abs': abs(net_balance),
        }

    # Extract debtors (net_balance < 0) and creditors (net_balance > 0)
    debtors = []
    creditors = []
    for member_id, data in balances.items():
        val = data['net_balance'].quantize(Decimal('0.01'))
        if val < Decimal('-0.005'):
            debtors.append({'id': member_id, 'balance': val})
        elif val > Decimal('0.005'):
            creditors.append({'id': member_id, 'balance': val})

    # Sort to optimize transactions (greedy simplification)
    debtors.sort(key=lambda x: x['balance'])  # Most negative first
    creditors.sort(key=lambda x: x['balance'], reverse=True)  # Most positive first

    recommended = []
    d_idx = 0
    c_idx = 0
    while d_idx < len(debtors) and c_idx < len(creditors):
        d = debtors[d_idx]
        c = creditors[c_idx]

        d_amt = -d['balance']
        c_amt = c['balance']

        settle_amt = min(d_amt, c_amt).quantize(Decimal('0.01'))
        if settle_amt > Decimal('0.00'):
            recommended.append((d['id'], c['id'], settle_amt))

        d['balance'] += settle_amt
        c['balance'] -= settle_amt

        if d['balance'].quantize(Decimal('0.01')) >= Decimal('-0.005'):
            d_idx += 1
        if c['balance'].quantize(Decimal('0.01')) <= Decimal('0.005'):
            c_idx += 1

    # Sync recommendations into the database as pending settlements
    active_pending_ids = []
    for payer_id, payee_id, amount in recommended:
        payer = Member.objects.get(id=payer_id)
        payee = Member.objects.get(id=payee_id)
        
        # Look for existing pending settlement
        settlement, created = Settlement.objects.get_or_create(
            group=group,
            payer=payer,
            payee=payee,
            status='pending',
            defaults={'amount': amount}
        )
        if not created:
            if settlement.amount != amount:
                settlement.amount = amount
                settlement.save()
        active_pending_ids.append(settlement.id)

    # Delete any pending settlements that are no longer recommended
    Settlement.objects.filter(group=group, status='pending').exclude(id__in=active_pending_ids).delete()

    return list(balances.values())


@login_required(login_url='login')
def balance_dashboard_view(request, group_pk):
    """
    View to display the balance dashboard for a specific group.
    Lists total paid, owes, receivable, and net balance for each member,
    along with automatically calculated recommended settlements.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    
    # Calculate balances and sync recommended settlements
    member_balances = recalculate_group_settlements(group)
    
    # Get all active pending settlements for this group
    pending_settlements = group.settlements.filter(status='pending').order_by('payer__name')
    
    return render(request, 'expenses/balance_dashboard.html', {
        'group': group,
        'member_balances': member_balances,
        'pending_settlements': pending_settlements,
    })


@login_required(login_url='login')
def member_balance_view(request, group_pk, member_pk):
    """
    View details of an individual group member's transactions, owes, and settlement history.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    member = get_object_or_404(Member, pk=member_pk, group=group)
    
    # Calculate all balances
    all_balances = recalculate_group_settlements(group)
    
    # Extract this member's summary
    member_summary = None
    for b in all_balances:
        if b['member'].id == member.id:
            member_summary = b
            break
            
    # Fetch expenses paid by this member
    expenses_paid = Expense.objects.filter(group=group, paid_by=member).order_by('-date')
    
    # Fetch expense splits this member owes
    splits_owed = ExpenseSplit.objects.filter(expense__group=group, member=member).order_by('-expense__date')
    
    # Fetch settlements this member participated in
    settlements_sent = Settlement.objects.filter(group=group, payer=member).order_by('-date')
    settlements_received = Settlement.objects.filter(group=group, payee=member).order_by('-date')
    
    return render(request, 'expenses/member_balance.html', {
        'group': group,
        'member': member,
        'summary': member_summary,
        'expenses_paid': expenses_paid,
        'splits_owed': splits_owed,
        'settlements_sent': settlements_sent,
        'settlements_received': settlements_received,
    })


@login_required(login_url='login')
def settlement_list_view(request, group_pk):
    """
    View completed and pending settlements for a group.
    Allows filtering by status (all, completed, pending).
    Also embeds a form to manually record a new settlement.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    
    # Recalculate to make sure pending settlements are up-to-date
    recalculate_group_settlements(group)
    
    status_filter = request.GET.get('status', 'all')
    settlements = group.settlements.all().order_by('-date')
    
    if status_filter == 'completed':
        settlements = settlements.filter(status='completed')
    elif status_filter == 'pending':
        settlements = settlements.filter(status='pending')
        
    # Manual Settlement creation form
    if request.method == 'POST':
        form = SettlementForm(request.POST, group=group)
        if form.is_valid():
            settlement = form.save(commit=False)
            settlement.group = group
            settlement.save()
            messages.success(request, "Settlement recorded successfully!")
            return redirect('settlement_list', group_pk=group.pk)
        else:
            messages.error(request, "Error recording settlement.")
    else:
        form = SettlementForm(group=group)
        
    return render(request, 'expenses/settlement_list.html', {
        'group': group,
        'settlements': settlements,
        'status_filter': status_filter,
        'form': form,
    })


@login_required(login_url='login')
def settlement_detail_view(request, group_pk, settlement_pk):
    """
    Display details of a specific settlement record.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    settlement = get_object_or_404(Settlement, pk=settlement_pk, group=group)
    return render(request, 'expenses/settlement_detail.html', {
        'group': group,
        'settlement': settlement,
    })


@login_required(login_url='login')
def settlement_confirm_view(request, group_pk, settlement_pk):
    """
    Confirm marking a pending settlement as completed.
    Validation rule: Completed settlement cannot be edited.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    settlement = get_object_or_404(Settlement, pk=settlement_pk, group=group)
    
    if settlement.status == 'completed':
        messages.warning(request, "This settlement is already completed and cannot be modified.")
        return redirect('settlement_detail', group_pk=group.pk, settlement_pk=settlement.pk)
        
    if request.method == 'POST':
        settlement.status = 'completed'
        settlement.save()
        messages.success(request, f"Settlement of ₹{settlement.amount} marked as Completed!")
        return redirect('settlement_list', group_pk=group.pk)
        
    return render(request, 'expenses/settlement_confirm.html', {
        'group': group,
        'settlement': settlement,
    })


@login_required(login_url='login')
def settlement_complete_view(request, group_pk, settlement_pk):
    """
    Quick action to mark a settlement as completed directly.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    settlement = get_object_or_404(Settlement, pk=settlement_pk, group=group)
    
    if settlement.status == 'completed':
        messages.warning(request, "This settlement is already completed.")
        return redirect('settlement_list', group_pk=group.pk)
        
    settlement.status = 'completed'
    settlement.save()
    messages.success(request, f"Settlement of ₹{settlement.amount} from {settlement.payer.name} to {settlement.payee.name} marked as Completed!")
    return redirect('settlement_list', group_pk=group.pk)



