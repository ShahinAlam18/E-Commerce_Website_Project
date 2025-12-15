from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm, AdminRegistrationForm
from .models import UserProfile


def login_view(request):
    # Redirect if user is already logged in
    if request.user.is_authenticated:
        return redirect('products:home')
        
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username_or_email, password=password)
        if not user:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            messages.success(request, 'Logged in successfully')
            return redirect('products:home')
        messages.error(request, 'Invalid credentials')

    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    request.session.flush()
    return redirect('accounts:login')


def register_view(request):
    """Handle both user and admin registration"""
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_type == 'admin':
            form = AdminRegistrationForm(request.POST)
        else:
            form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please log in.')
            
            # Send welcome email for regular users
            if not user_type == 'admin':
                try:
                    send_mail(
                        subject='Welcome to ShopX',
                        message='Hi, your registration at ShopX was successful. Happy shopping!',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass  # Silently handle email sending failures
            
            return redirect('accounts:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
    })
