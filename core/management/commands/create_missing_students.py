# core/management/commands/create_missing_students.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Student
import random
import string

class Command(BaseCommand):
    help = 'Create Student profiles for users who don\'t have them'

    def handle(self, *args, **options):
        users_without_students = User.objects.filter(student__isnull=True)
        
        for user in users_without_students:
            qr_code = f"LL{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
            student_id = f"S{''.join(random.choices(string.digits, k=6))}"
            
            Student.objects.create(
                user=user,
                student_id=student_id,
                room_number="",
                phone_number="",
                qr_code=qr_code
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created Student profile for {user.username}')
            )