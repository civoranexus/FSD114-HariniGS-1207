from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test users for the application'

    def handle(self, *args, **options):
        # Test Student
        if not User.objects.filter(username='student1').exists():
            student = User.objects.create_user(
                username='student1',
                email='student1@example.com',
                password='password123'
            )
            profile = Profile.objects.get(user=student)
            profile.role = 'student'
            profile.save()
            self.stdout.write(self.style.SUCCESS('Created test student: student1 / password123'))
        else:
            self.stdout.write(self.style.WARNING('Student user already exists'))

        # Test Teacher
        if not User.objects.filter(username='teacher1').exists():
            teacher = User.objects.create_user(
                username='teacher1',
                email='teacher1@example.com',
                password='password123'
            )
            profile = Profile.objects.get(user=teacher)
            profile.role = 'teacher'
            profile.save()
            self.stdout.write(self.style.SUCCESS('Created test teacher: teacher1 / password123'))
        else:
            self.stdout.write(self.style.WARNING('Teacher user already exists'))

        # Test Admin
        if not User.objects.filter(username='admin1').exists():
            admin = User.objects.create_superuser(
                username='admin1',
                email='admin1@example.com',
                password='password123'
            )
            profile = Profile.objects.get(user=admin)
            profile.role = 'admin'
            profile.save()
            self.stdout.write(self.style.SUCCESS('Created test admin: admin1 / password123'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))
