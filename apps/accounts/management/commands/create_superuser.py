from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser if one does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(email='admin@example.com').exists():
            try:
                User.objects.create_superuser(
                    username='admin@example.com',  # Include username
                    email='admin@example.com',
                    first_name='Admin',
                    last_name='User',
                    password='adminpassword'
                )
                self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating superuser: {e}'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists'))
