from django import template

register = template.Library()

@register.filter
def is_admin(user):
    """Check if user is admin, with fallback for missing UserProfile"""
    if not user.is_authenticated:
        return False
    
    try:
        return user.profile.is_admin or user.is_superuser
    except:
        # Fallback to superuser if UserProfile doesn't exist
        return user.is_superuser

@register.filter
def has_profile(user):
    """Check if user has a profile"""
    if not user.is_authenticated:
        return False
    
    try:
        user.profile
        return True
    except:
        return False
