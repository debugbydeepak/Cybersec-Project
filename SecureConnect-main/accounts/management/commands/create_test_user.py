from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import AuditLog

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a test user for SECUREWAY application'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='testuser', help='Username for test user')
        parser.add_argument('--email', type=str, default='testuser@secureway.com', help='Email for test user')
        parser.add_argument('--password', type=str, default='testpass123', help='Password for test user')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists.')
            )
            user = User.objects.get(username=username)
        else:
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create audit log for user creation
            AuditLog.objects.create(
                user=user,
                action='Test user created via management command',
                ip_address='127.0.0.1',
                details={'command': 'create_test_user', 'username': username}
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created test user "{username}"')
            )

        # Display user information
        self.stdout.write('\n' + '='*50)
        self.stdout.write('TEST USER CREDENTIALS:')
        self.stdout.write('='*50)
        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'User ID: {user.id}')
        self.stdout.write('='*50)
        self.stdout.write('\nYou can now login with these credentials at:')
        self.stdout.write('http://localhost:8080/accounts/login/')
