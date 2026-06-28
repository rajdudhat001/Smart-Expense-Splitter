from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
