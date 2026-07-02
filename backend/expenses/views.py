from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, GroupForm, MemberForm
from .models import Group, Member

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
            messages.success(request, "Group created successfully! / ग्रुप सफलतापूर्वक बनाया गया!")
            return redirect('group_list')
        else:
            messages.error(request, "Error creating group. Please fix the errors below. / ग्रुप बनाने में त्रुटि। कृपया नीचे दिए गए एरर्स को सुधारें।")
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
            messages.success(request, "Group updated successfully! / ग्रुप सफलतापूर्वक अपडेट किया गया!")
            return redirect('group_list')
        else:
            messages.error(request, "Error updating group. Please fix the errors below. / ग्रुप अपडेट करने में त्रुटि। कृपया नीचे दिए गए एरर्स को सुधारें।")
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
        messages.success(request, "Group deleted successfully! / ग्रुप सफलतापूर्वक हटा दिया गया!")
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
            messages.success(request, "Member added successfully! / सदस्य सफलतापूर्वक जोड़ा गया!")
            return redirect('member_list', group_pk=group.pk)
        else:
            messages.error(request, "Error adding member. Please fix the errors below. / सदस्य जोड़ने में त्रुटि। कृपया नीचे दिए गए एरर्स को सुधारें।")
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
            messages.success(request, "Member updated successfully! / सदस्य सफलतापूर्वक अपडेट किया गया!")
            return redirect('member_list', group_pk=group.pk)
        else:
            messages.error(request, "Error updating member. Please fix the errors below. / सदस्य अपडेट करने में त्रुटि। कृपया नीचे दिए गए एरर्स को सुधारें।")
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
        messages.success(request, f"Member '{member_name}' removed successfully! / सदस्य '{member_name}' सफलतापूर्वक हटा दिया गया!")
        return redirect('member_list', group_pk=group.pk)
    return render(request, 'expenses/member_delete.html', {'group': group, 'member': member})


