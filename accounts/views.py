from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

from accounts.models import UserProfile

def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            user_profile = user.profile  
            if user_profile.suspended:
                messages.error(request, "Your account has been suspended. Please contact support.")
                return redirect('login')

            login(request, user)  
            messages.success(request, f"Welcome back, {user.first_name}!")

            # Check the usertype to redirect to the correct dashboard
            if user_profile.usertype == 'admin':
                return redirect('administration_admin_dashboard') 
            else:
                return redirect('portal_user_dashboard') 
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')


def register(request):
    """Show the registration form and handle user registration."""
    if request.method == 'POST':
        # Retrieve form data
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        contact = request.POST['contact']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Prepare context with user data to retain input
        context = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'contact': contact,
            'email': email,
        }

        # Validate passwords
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/register.html', context)

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'accounts/register.html', context)

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already in use')
            return render(request, 'accounts/register.html', context)

        if not messages.get_messages(request):
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            user.save()

            # Create UserProfile instance and save contact information
            user_profile = UserProfile.objects.create(
                user=user,
                usertype='user',
                contact=contact,  # Save contact information
            )
            user_profile.save()

            messages.success(request, 'Your account has been created successfully. You can now log in.')
            return redirect('login')  

    else:
        context = {}

    return render(request, 'accounts/register.html', context)

def logout_view(request):
    """Log out the user and redirect to the home page."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('kazilink_home') 

