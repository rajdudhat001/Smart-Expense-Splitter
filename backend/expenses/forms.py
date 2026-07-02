from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Group, Member, Expense


class UserRegistrationForm(forms.ModelForm):
    # Password field with PasswordInput widget to hide characters
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password'
        }),
        help_text="Required. Use a strong password."
    )
    # Confirm password field to verify the user typed it correctly
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter Email'
            }),
        }

    def clean_email(self):
        """
        Validate that the email address is unique in the database.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email is already registered. / यह ईमेल पहले से ही रजिस्टर्ड है।")
        return email

    def clean(self):
        """
        Validate that the passwords entered in both fields match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            # Raise validation error if passwords do not match
            self.add_error('confirm_password', "Passwords do not match. / पासवर्ड मेल नहीं खाते हैं।")
        
        return cleaned_data

    def save(self, commit=True):
        """
        Overriding the save method to set the hashed password correctly.
        """
        user = super().save(commit=False)
        # set_password hashes the raw password string before saving
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    # Username and password fields for logging in
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password'
        })
    )


class GroupForm(forms.ModelForm):
    """
    Form for creating and updating Groups.
    """
    class Meta:
        model = Group
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Group Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Group Description',
                'rows': 3
            }),
        }

    def clean_name(self):
        """
        Validate that the group name is not too short.
        """
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 3:
            raise ValidationError("Group name must be at least 3 characters long. / ग्रुप का नाम कम से कम 3 अक्षरों का होना चाहिए।")
        return name.strip()


class MemberForm(forms.ModelForm):
    """
    Form for creating and updating members of a group.
    """
    class Meta:
        model = Member
        fields = ['name', 'email', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Member Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Email (Optional)'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Phone Number (Optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        # We pass 'group' from views to perform uniqueness validation within that group
        self.group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 2:
            raise ValidationError("Member name must be at least 2 characters long. / सदस्य का नाम कम से कम 2 अक्षरों का होना चाहिए।")
        
        name = name.strip()
        if self.group:
            # Check for duplicate names (case-insensitive) in the same group
            query = Member.objects.filter(group=self.group, name__iexact=name)
            # Exclude current member if updating
            if self.instance and self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise ValidationError("A member with this name already exists in this group. / इस ग्रुप में इस नाम का सदस्य पहले से ही मौजूद है।")
        return name


class ExpenseForm(forms.ModelForm):
    """
    Form for creating and updating Expenses.
    Filters the paid_by field to show only members of the selected group.
    """
    class Meta:
        model = Expense
        fields = ['title', 'description', 'amount', 'paid_by', 'date', 'category', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Expense Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Expense Description (Optional)',
                'rows': 2
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Amount',
                'step': '0.01'
            }),
            'paid_by': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Category (e.g., Food, Travel)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Notes (Optional)',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        # We pass 'group' from views to filter the paid_by dropdown options
        self.group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        if self.group:
            self.fields['paid_by'].queryset = Member.objects.filter(group=self.group).order_by('name')

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise ValidationError("Expense amount must be greater than zero. / खर्चे की राशि शून्य से अधिक होनी चाहिए।")
        return amount



