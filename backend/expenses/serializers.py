from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Group, Member, Expense, ExpenseSplit, Settlement, Budget, Invitation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class GroupSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'created_by', 'members', 'created_at']
        read_only_fields = ['created_at']

    def validate_name(self, value):
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("Group name must be at least 3 characters long.")
        return value.strip()

class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ['id', 'group', 'user', 'name', 'email', 'phone', 'created_at']
        read_only_fields = ['group', 'user', 'created_at']

    def validate_name(self, value):
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Member name must be at least 2 characters long.")
        return value.strip()

    def validate(self, data):
        name = data.get('name', '').strip()
        group = self.context.get('group') or (self.instance.group if self.instance else None)
        
        if group and name:
            query = Member.objects.filter(group=group, name__iexact=name)
            if self.instance and self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise serializers.ValidationError({"name": "A member with this name already exists in this group."})
        
        return data

class ExpenseSerializer(serializers.ModelSerializer):
    paid_by_name = serializers.CharField(source='paid_by.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'group', 'title', 'description', 'amount', 
            'paid_by', 'paid_by_name', 'date', 'category', 
            'notes', 'created_by', 'created_by_username', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['group', 'created_by', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Expense amount must be greater than zero.")
        return value

class ExpenseSplitSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.name', read_only=True)

    class Meta:
        model = ExpenseSplit
        fields = ['id', 'expense', 'member', 'member_name', 'amount', 'is_settled']
        read_only_fields = ['expense']

class SettlementSerializer(serializers.ModelSerializer):
    payer_name = serializers.CharField(source='payer.name', read_only=True)
    payee_name = serializers.CharField(source='payee.name', read_only=True)

    class Meta:
        model = Settlement
        fields = ['id', 'group', 'payer', 'payer_name', 'payee', 'payee_name', 'amount', 'date', 'status']
        read_only_fields = ['group', 'date']

    def validate_amount(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Settlement amount must be greater than zero.")
        return value

    def validate(self, data):
        payer = data.get('payer')
        payee = data.get('payee')
        amount = data.get('amount')
        status = data.get('status', 'pending')
        group = self.context.get('group') or (self.instance.group if self.instance else None)

        if payer and payee and payer == payee:
            raise serializers.ValidationError({"payee": "Payer and payee cannot be the same member."})

        # Check for duplicate settlements
        if payer and payee and amount and group:
            exclude_pk = self.instance.pk if self.instance and self.instance.pk else None
            duplicates = Settlement.objects.filter(
                group=group,
                payer=payer,
                payee=payee,
                amount=amount,
                status=status
            )
            if exclude_pk:
                duplicates = duplicates.exclude(pk=exclude_pk)
            if duplicates.exists():
                raise serializers.ValidationError("An identical settlement record already exists.")

        return data

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'group', 'user', 'amount_limit', 'created_at']
        read_only_fields = ['group', 'user', 'created_at']

class InvitationSerializer(serializers.ModelSerializer):
    invited_by_username = serializers.CharField(source='invited_by.username', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = Invitation
        fields = ['id', 'group', 'group_name', 'email', 'invited_by', 'invited_by_username', 'status', 'created_at']
        read_only_fields = ['invited_by', 'status', 'created_at']
