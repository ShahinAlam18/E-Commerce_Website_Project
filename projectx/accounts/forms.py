from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
from products.models import Product  # Add this import


class UserRegistrationForm(UserCreationForm):
    """Form for regular user registration"""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.get_or_create(user=user, defaults={'is_admin': False})
       

class AdminRegistrationForm(UserCreationForm):
    """Form for admin registration with password verification"""
    email = forms.EmailField(required=True)
    admin_password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput,
        help_text="Enter the admin password to register as admin"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'admin_password')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['admin_password'].widget.attrs.update({'class': 'form-control'})
    
    def clean_admin_password(self):
        admin_password = self.cleaned_data.get('admin_password')
        if admin_password != '11814':
            raise forms.ValidationError('Invalid admin password. Only authorized personnel can register as admin.')
        return admin_password
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
            # Create admin profile with admin privileges
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'is_admin': True}
            )
            if not created and not profile.is_admin:
                profile.is_admin = True
                profile.save()
        return user
