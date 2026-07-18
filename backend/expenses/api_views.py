from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import models
from decimal import Decimal, ROUND_DOWN

from .models import Group, Member, Expense, ExpenseSplit, Settlement, Budget, Invitation
from .serializers import (
    UserSerializer, RegisterSerializer, GroupSerializer, 
    MemberSerializer, ExpenseSerializer, ExpenseSplitSerializer, 
    SettlementSerializer, BudgetSerializer, InvitationSerializer
)
from .views import recalculate_group_settlements

# --- Authentication APIs ---

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """
    Register a new user and return user details and authentication token.
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """
    Authenticate user credentials and return authentication token.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'detail': 'Please provide both username and password.'}, status=status.HTTP_400_BAD_REQUEST)
        
    user = authenticate(username=username, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """
    Logout user by deleting current auth token.
    """
    request.user.auth_token.delete()
    return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_me(request):
    """
    Retrieve details of current authenticated user.
    """
    return Response(UserSerializer(request.user).data)


# --- Group Management APIs ---

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def group_list_create(request):
    """
    GET: List all groups where the user is a creator or member.
    POST: Create a new group and add the user as creator & member.
    """
    if request.method == 'GET':
        # Retrieve groups where request.user is creator OR member
        groups = Group.objects.filter(
            models.Q(created_by=request.user) | models.Q(members=request.user)
        ).distinct().order_by('-created_at')
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save(created_by=request.user)
            group.members.add(request.user)
            # Optionally auto-create a member profile for the creator in the group members
            Member.objects.get_or_create(
                group=group,
                name=request.user.username,
                defaults={'email': request.user.email}
            )
            return Response(GroupSerializer(group).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def group_detail_update_delete(request, pk):
    """
    Retrieve, update, or delete a group. Requires being the creator.
    """
    group = get_object_or_404(Group, pk=pk, created_by=request.user)
    
    if request.method == 'GET':
        return Response(GroupSerializer(group).data)
        
    elif request.method in ['PUT', 'PATCH']:
        partial = (request.method == 'PATCH')
        serializer = GroupSerializer(group, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'DELETE':
        group.delete()
        return Response({'detail': 'Group deleted successfully.'}, status=status.HTTP_200_OK)


# --- Member Management APIs ---

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def member_list_create(request, group_pk):
    """
    GET: List all members of a group.
    POST: Add a member to a group. Requires group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    
    if request.method == 'GET':
        members = group.group_members.all().order_by('name')
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = MemberSerializer(data=request.data, context={'group': group})
        if serializer.is_valid():
            member = serializer.save(group=group)
            return Response(MemberSerializer(member).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def member_detail_update_delete(request, group_pk, pk):
    """
    Update or delete a group member. Requires group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    member = get_object_or_404(Member, pk=pk, group=group)
    
    if request.method in ['PUT', 'PATCH']:
        partial = (request.method == 'PATCH')
        serializer = MemberSerializer(member, data=request.data, partial=partial, context={'group': group})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'DELETE':
        member_name = member.name
        member.delete()
        return Response({'detail': f"Member '{member_name}' removed successfully."}, status=status.HTTP_200_OK)


# --- Expense Management APIs ---

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def expense_list_create(request, group_pk):
    """
    GET: List all expenses inside a group with the total sum.
    POST: Create a new expense. Requires group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    
    if request.method == 'GET':
        expenses = group.expenses.all().order_by('-date', '-created_at')
        serializer = ExpenseSerializer(expenses, many=True)
        total_amount = sum(expense.amount for expense in expenses)
        return Response({
            'expenses': serializer.data,
            'total_amount': total_amount
        })
        
    elif request.method == 'POST':
        if not group.group_members.exists():
            return Response({'detail': 'Please add at least one member to the group before adding expenses.'}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            # Validate paid_by member belongs to the group
            paid_by = serializer.validated_data.get('paid_by')
            if paid_by.group != group:
                return Response({'paid_by': 'Paid by member must belong to the same group.'}, status=status.HTTP_400_BAD_REQUEST)
                
            expense = serializer.save(group=group, created_by=request.user)
            return Response(ExpenseSerializer(expense).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def expense_detail_update_delete(request, group_pk, pk):
    """
    Retrieve details of an expense (including split info), update, or delete it.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    expense = get_object_or_404(Expense, pk=pk, group=group)
    
    if request.method == 'GET':
        expense_data = ExpenseSerializer(expense).data
        splits = expense.splits.all().order_by('member__name')
        splits_data = ExpenseSplitSerializer(splits, many=True).data
        expense_data['splits'] = splits_data
        return Response(expense_data)
        
    elif request.method in ['PUT', 'PATCH']:
        partial = (request.method == 'PATCH')
        serializer = ExpenseSerializer(expense, data=request.data, partial=partial)
        if serializer.is_valid():
            if 'paid_by' in serializer.validated_data:
                paid_by = serializer.validated_data.get('paid_by')
                if paid_by.group != group:
                    return Response({'paid_by': 'Paid by member must belong to the same group.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'DELETE':
        expense.delete()
        return Response({'detail': 'Expense deleted successfully.'}, status=status.HTTP_200_OK)


# --- Expense Splitting APIs ---

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def preview_equal_split(request, group_pk, expense_pk):
    """
    Given a list of member IDs in request.data['member_ids'], calculate the equal splits without saving.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    expense = get_object_or_404(Expense, pk=expense_pk, group=group)
    
    selected_ids = request.data.get('member_ids', [])
    if not selected_ids:
        return Response({'detail': 'Please select at least one member.'}, status=status.HTTP_400_BAD_REQUEST)
        
    selected_members = list(Member.objects.filter(id__in=selected_ids, group=group).order_by('name'))
    if len(selected_members) != len(selected_ids):
        return Response({'detail': 'Invalid members provided.'}, status=status.HTTP_400_BAD_REQUEST)
        
    total_amount = Decimal(str(expense.amount))
    n = len(selected_members)
    
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
            'member_id': m.id,
            'member_name': m.name,
            'amount': amount
        })
        
    return Response(splits_preview)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_expense_splits(request, group_pk, expense_pk):
    """
    Save splits for an expense.
    Request body:
    {
      "split_method": "equal" | "unequal",
      "splits": [{"member_id": 1, "amount": 30.00}, ...]
    }
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    expense = get_object_or_404(Expense, pk=expense_pk, group=group)
    
    split_method = request.data.get('split_method')
    splits_input = request.data.get('splits', [])
    
    if not split_method or split_method not in ['equal', 'unequal']:
        return Response({'detail': 'Invalid or missing split method.'}, status=status.HTTP_400_BAD_REQUEST)
        
    if not splits_input:
        return Response({'detail': 'Please provide splits details.'}, status=status.HTTP_400_BAD_REQUEST)
        
    # Verify all members in splits belong to the group
    member_ids = [s.get('member_id') for s in splits_input]
    db_members = list(Member.objects.filter(id__in=member_ids, group=group))
    if len(db_members) != len(member_ids):
        return Response({'detail': 'Some members do not belong to this group.'}, status=status.HTTP_400_BAD_REQUEST)
        
    # Validation rules:
    total_expense = Decimal(str(expense.amount))
    total_entered = Decimal('0.00')
    entered_shares = {}
    
    for s in splits_input:
        m_id = s.get('member_id')
        try:
            val = Decimal(str(s.get('amount', '0.00')))
            if val < 0:
                return Response({'detail': 'Split amounts cannot be negative.'}, status=status.HTTP_400_BAD_REQUEST)
            if val > total_expense:
                return Response({'detail': 'Split amount cannot exceed total expense.'}, status=status.HTTP_400_BAD_REQUEST)
            entered_shares[m_id] = val
            total_entered += val
        except (ValueError, TypeError):
            return Response({'detail': 'Invalid split amount entered.'}, status=status.HTTP_400_BAD_REQUEST)
            
    # Verify total sum of splits equals expense amount
    diff = abs(total_expense - total_entered)
    if diff >= Decimal('0.01'):
        return Response({
            'detail': f"Total split amounts (₹{total_entered:.2f}) must exactly equal total expense (₹{total_expense:.2f}). Diff: ₹{(total_expense - total_entered):.2f}"
        }, status=status.HTTP_400_BAD_REQUEST)
        
    # 1. Clear old splits
    ExpenseSplit.objects.filter(expense=expense).delete()
    
    # 2. Save splits: members in input get calculated/entered shares, other group members get 0.00
    all_group_members = group.group_members.all()
    created_splits = []
    for m in all_group_members:
        share_amount = entered_shares.get(m.id, Decimal('0.00'))
        split = ExpenseSplit.objects.create(
            expense=expense,
            member=m,
            amount=share_amount
        )
        created_splits.append(split)
        
    serializer = ExpenseSplitSerializer(created_splits, many=True)
    return Response({
        'detail': 'Splits saved successfully.',
        'splits': serializer.data
    }, status=status.HTTP_200_OK)


# --- Balances & Settlements APIs ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def group_balances(request, group_pk):
    """
    GET: Calculate balances and return active member net balances and recommended smart settlements.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    
    # Calculate balances and sync recommended settlements
    member_balances = recalculate_group_settlements(group)
    
    # Format response: serialize member objects inside balances
    formatted_balances = []
    for b in member_balances:
        formatted_balances.append({
            'member': MemberSerializer(b['member']).data,
            'paid': b['paid'],
            'owes': b['owes'],
            'receivable': b['receivable'],
            'net_balance': b['net_balance']
        })
        
    # Get active pending settlements
    pending_settlements = group.settlements.filter(status='pending').order_by('payer__name')
    pending_data = SettlementSerializer(pending_settlements, many=True).data
    
    return Response({
        'balances': formatted_balances,
        'recommended_settlements': pending_data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def member_ledger(request, group_pk, member_pk):
    """
    GET: Get detailed transaction history for a single group member.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    member = get_object_or_404(Member, pk=member_pk, group=group)
    
    # Recalculate balances
    all_balances = recalculate_group_settlements(group)
    member_summary = None
    for b in all_balances:
        if b['member'].id == member.id:
            member_summary = {
                'paid': b['paid'],
                'owes': b['owes'],
                'receivable': b['receivable'],
                'net_balance': b['net_balance']
            }
            break
            
    # Fetch data
    expenses_paid = Expense.objects.filter(group=group, paid_by=member).order_by('-date')
    splits_owed = ExpenseSplit.objects.filter(expense__group=group, member=member).order_by('-expense__date')
    settlements_sent = Settlement.objects.filter(group=group, payer=member).order_by('-date')
    settlements_received = Settlement.objects.filter(group=group, payee=member).order_by('-date')
    
    # Format response
    return Response({
        'member': MemberSerializer(member).data,
        'summary': member_summary,
        'expenses_paid': ExpenseSerializer(expenses_paid, many=True).data,
        'splits_owed': ExpenseSplitSerializer(splits_owed, many=True).data,
        'settlements_sent': SettlementSerializer(settlements_sent, many=True).data,
        'settlements_received': SettlementSerializer(settlements_received, many=True).data,
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def settlement_list_create(request, group_pk):
    """
    GET: List all settlements of a group (filter by status completed/pending).
    POST: Record a manual settlement. Requires group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    
    # Recalculate to make sure pending recommendations are up to date
    recalculate_group_settlements(group)
    
    if request.method == 'GET':
        status_filter = request.query_params.get('status', 'all')
        settlements = group.settlements.all().order_by('-date')
        
        if status_filter == 'completed':
            settlements = settlements.filter(status='completed')
        elif status_filter == 'pending':
            settlements = settlements.filter(status='pending')
            
        serializer = SettlementSerializer(settlements, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = SettlementSerializer(data=request.data, context={'group': group})
        if serializer.is_valid():
            # Validate payer and payee belong to the group
            payer = serializer.validated_data.get('payer')
            payee = serializer.validated_data.get('payee')
            if payer.group != group or payee.group != group:
                return Response({'detail': 'Payer and payee must belong to the group.'}, status=status.HTTP_400_BAD_REQUEST)
                
            settlement = serializer.save(group=group)
            return Response(SettlementSerializer(settlement).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_settlement(request, group_pk, pk):
    """
    POST: Mark a pending settlement as completed.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    settlement = get_object_or_404(Settlement, pk=pk, group=group)
    
    if settlement.status == 'completed':
        return Response({'detail': 'This settlement is already completed.'}, status=status.HTTP_400_BAD_REQUEST)
        
    settlement.status = 'completed'
    settlement.save()
    return Response({
        'detail': 'Settlement marked as completed.',
        'settlement': SettlementSerializer(settlement).data
    }, status=status.HTTP_200_OK)


# --- Budget Configuration APIs ---

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def group_budget(request, group_pk):
    """
    GET: Retrieve the group budget limit and the total group spending (to compare/alert).
    POST: Set or update the budget limit. Requires group creator.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    budget = Budget.objects.filter(group=group).first()
    
    if request.method == 'GET':
        budget_data = BudgetSerializer(budget).data if budget else None
        
        # Calculate sum total of expenses in the group
        expenses = group.expenses.all()
        total_spending = sum(expense.amount for expense in expenses)
        
        is_exceeded = False
        if budget and total_spending > budget.amount_limit:
            is_exceeded = True
            
        return Response({
            'budget': budget_data,
            'total_spending': total_spending,
            'is_exceeded': is_exceeded
        })
        
    elif request.method == 'POST':
        limit = request.data.get('amount_limit')
        if limit is None or Decimal(str(limit)) <= 0:
            return Response({'amount_limit': 'Amount limit must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if budget:
            budget.amount_limit = Decimal(str(limit))
            budget.save()
        else:
            budget = Budget.objects.create(group=group, amount_limit=Decimal(str(limit)))
            
        return Response(BudgetSerializer(budget).data, status=status.HTTP_200_OK)


# --- Group Invitation APIs ---

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_member(request, group_pk):
    """
    POST: Invite a member by email to join the group. Only the group creator can invite.
    """
    group = get_object_or_404(Group, pk=group_pk, created_by=request.user)
    email = request.data.get('email', '').strip()
    
    if not email:
        return Response({'email': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
    # Check if this email is already invited to this group
    if Invitation.objects.filter(group=group, email__iexact=email).exists():
        return Response({'email': 'This email has already been invited to this group.'}, status=status.HTTP_400_BAD_REQUEST)
        
    # Create the invitation
    invitation = Invitation.objects.create(
        group=group,
        email=email,
        invited_by=request.user,
        status='pending'
    )
    
    return Response(InvitationSerializer(invitation).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_invitations(request):
    """
    GET: List all pending invitations for the current user.
    """
    invitations = Invitation.objects.filter(
        email__iexact=request.user.email,
        status='pending'
    ).order_by('-created_at')
    
    serializer = InvitationSerializer(invitations, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_invitation(request, pk):
    """
    POST: Accept a pending group invitation.
    """
    invitation = get_object_or_404(Invitation, pk=pk, email__iexact=request.user.email, status='pending')
    group = invitation.group
    
    # Add user to the group ManyToMany members list
    group.members.add(request.user)
    
    # Mark invitation as accepted
    invitation.status = 'accepted'
    invitation.save()
    
    # Check if a Member profile with this email already exists in this group.
    # If yes, link it to this user so history is unified!
    member = Member.objects.filter(group=group, email__iexact=request.user.email).first()
    if member:
        member.user = request.user
        member.save()
    else:
        # Create a new Member profile for this user in the group
        Member.objects.create(
            group=group,
            user=request.user,
            name=request.user.username,
            email=request.user.email
        )
        
    return Response({'detail': f'Joined group {group.name} successfully.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decline_invitation(request, pk):
    """
    POST: Decline a pending group invitation.
    """
    invitation = get_object_or_404(Invitation, pk=pk, email__iexact=request.user.email, status='pending')
    invitation.status = 'declined'
    invitation.save()
    return Response({'detail': 'Invitation declined successfully.'}, status=status.HTTP_200_OK)

