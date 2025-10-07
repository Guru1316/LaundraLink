# core/admin.py
from django.contrib import admin
from .models import *

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'room_number', 'wallet_balance']
    search_fields = ['student_id', 'user__username', 'room_number']

@admin.register(LaundryBag)
class LaundryBagAdmin(admin.ModelAdmin):
    list_display = ['qr_code', 'student', 'status', 'request_date']
    list_filter = ['status', 'request_date']
    search_fields = ['qr_code', 'student__student_id']

@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    list_display = ['category', 'color', 'description', 'is_claimed', 'date_found']
    list_filter = ['category', 'color', 'is_claimed', 'date_found']
    search_fields = ['description', 'location_found']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'title']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'payment_date', 'transaction_id']
    list_filter = ['payment_date']
    search_fields = ['student__student_id', 'transaction_id']