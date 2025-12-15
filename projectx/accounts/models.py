from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """User profile with admin status"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_admin = models.BooleanField(default=False, help_text="Designates whether this user is an admin")
    
    def __str__(self):
        return f"{self.user.username} - {'Admin' if self.is_admin else 'User'}"
    
    @property
    def username(self):
        return self.user.username
    
    @property
    def email(self):
        return self.user.email
