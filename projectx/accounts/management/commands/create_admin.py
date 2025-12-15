from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from products.models import Product

class Command(BaseCommand):
    help = 'Creates a superuser account with admin privileges'

    def handle(self, *args, **kwargs):
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'

        try:
            # Check if admin already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING('Admin user already exists'))
                return

            # Create superuser
            admin = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )

            # Create UserProfile
            UserProfile.objects.get_or_create(
                user=admin,
                defaults={'is_admin': True}
            )

            # Ensure all product permissions
            content_type = ContentType.objects.get_for_model(Product)
            permissions = Permission.objects.filter(content_type=content_type)
            for permission in permissions:
                admin.user_permissions.add(permission)

            self.stdout.write(self.style.SUCCESS(f'''
            Successfully created admin account!
            Username: {username}
            Password: {password}
            Email: {email}
            
            You can now log in at /admin/
            '''))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin: {str(e)}'))
