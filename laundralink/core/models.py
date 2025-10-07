# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    room_number = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    qr_code = models.CharField(max_length=100, unique=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"

class LaundryBag(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Pickup Requested'),
        ('picked_up', 'Picked Up'),
        ('washing', 'Washing'),
        ('drying', 'Drying'),
        ('ready', 'Ready for Pickup'),
        ('delivered', 'Delivered'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    qr_code = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    request_date = models.DateTimeField(auto_now_add=True)
    pickup_date = models.DateTimeField(null=True, blank=True)
    ready_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Bag {self.qr_code} - {self.student.student_id}"

class LostItem(models.Model):
    CATEGORY_CHOICES = [
        ('clothing', 'Clothing'),
        ('accessory', 'Accessory'),
        ('electronics', 'Electronics'),
        ('documents', 'Documents'),
        ('other', 'Other'),
    ]
    
    COLOR_CHOICES = [
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('black', 'Black'),
        ('white', 'White'),
        ('gray', 'Gray'),
        ('brown', 'Brown'),
        ('pink', 'Pink'),
        ('purple', 'Purple'),
        ('orange', 'Orange'),
        ('multi', 'Multi-colored'),
    ]
    
    found_by = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES)
    description = models.TextField()
    location_found = models.CharField(max_length=100)
    date_found = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='lost_items/', null=True, blank=True)
    is_claimed = models.BooleanField(default=False)
    claimed_by = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    date_claimed = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_color_display()} {self.get_category_display()}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=50, default='UPI')
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.student.student_id}"