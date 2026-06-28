from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm

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
                error_message = "Invalid username or password. / यूजरनेम या पासवर्ड गलत है।"
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
