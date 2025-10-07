# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.db.models import Q
from .models import *
import json
import random
import string
from django.utils import timezone

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create student profile with random QR code
            qr_code = f"LL{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
            student_id = f"S{''.join(random.choices(string.digits, k=6))}"
            
            Student.objects.create(
                user=user,
                student_id=student_id,
                room_number="",
                phone_number="",
                qr_code=qr_code
            )
            
            # Log the user in
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Helper function to get or create student
def get_or_create_student(user):
    try:
        return Student.objects.get(user=user)
    except Student.DoesNotExist:
        qr_code = f"LL{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        student_id = f"S{''.join(random.choices(string.digits, k=6))}"
        
        return Student.objects.create(
            user=user,
            student_id=student_id,
            room_number="",
            phone_number="",
            qr_code=qr_code
        )

@login_required
def dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
        laundry_bags = LaundryBag.objects.filter(student=student).order_by('-request_date')[:5]
        notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
        
        context = {
            'student': student,
            'laundry_bags': laundry_bags,
            'notifications': notifications,
        }
        return render(request, 'dashboard.html', context)
    except Student.DoesNotExist:
        # If student profile doesn't exist, create one
        qr_code = f"LL{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"
        student_id = f"S{''.join(random.choices(string.digits, k=6))}"
        
        student = Student.objects.create(
            user=request.user,
            student_id=student_id,
            room_number="",
            phone_number="",
            qr_code=qr_code
        )
        
        return redirect('dashboard')

@login_required
def request_laundry_pickup(request):
    student = get_or_create_student(request.user)
    
    if request.method == 'POST':
        qr_code = f"BAG{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"
        
        laundry_bag = LaundryBag.objects.create(
            student=student,
            qr_code=qr_code,
            status='requested'
        )
        
        # Create notification
        Notification.objects.create(
            user=request.user,
            title="Laundry Pickup Requested",
            message=f"Your laundry pickup has been requested. QR Code: {qr_code}"
        )
        
        return redirect('dashboard')
    
    return render(request, 'request_pickup.html')

@login_required
def track_laundry(request):
    student = get_or_create_student(request.user)
    laundry_bags = LaundryBag.objects.filter(student=student).order_by('-request_date')
    return render(request, 'track_laundry.html', {'laundry_bags': laundry_bags})

# Add the missing lost_found function
@login_required
def lost_found(request):
    student = get_or_create_student(request.user)
    lost_items = LostItem.objects.filter(is_claimed=False).order_by('-date_found')
    
    if request.method == 'POST':
        category = request.POST.get('category')
        color = request.POST.get('color')
        description = request.POST.get('description')
        location_found = request.POST.get('location_found')
        
        LostItem.objects.create(
            found_by=request.user,
            category=category,
            color=color,
            description=description,
            location_found=location_found
        )
        
        return redirect('lost_found')
    
    return render(request, 'lost_found.html', {'lost_items': lost_items})

@login_required
def search_lost_items(request):
    student = get_or_create_student(request.user)
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    color = request.GET.get('color', '')
    
    lost_items = LostItem.objects.filter(is_claimed=False)
    
    if query:
        lost_items = lost_items.filter(
            Q(description__icontains=query) |
            Q(location_found__icontains=query)
        )
    
    if category:
        lost_items = lost_items.filter(category=category)
    
    if color:
        lost_items = lost_items.filter(color=color)
    
    return render(request, 'search_lost_items.html', {
        'lost_items': lost_items,
        'query': query,
        'category': category,
        'color': color
    })

@login_required
def claim_item(request, item_id):
    student = get_or_create_student(request.user)
    item = get_object_or_404(LostItem, id=item_id)
    
    if request.method == 'POST':
        item.is_claimed = True
        item.claimed_by = student
        item.date_claimed = timezone.now()
        item.save()
        
        # Add reward points
        student.wallet_balance += 10  # 10 points reward
        student.save()
        
        Notification.objects.create(
            user=request.user,
            title="Item Claimed Successfully",
            message=f"You've claimed the {item.get_color_display()} {item.get_category_display()}. 10 reward points added to your wallet!"
        )
        
        return redirect('lost_found')
    
    return render(request, 'claim_item.html', {'item': item})

@login_required
def wallet(request):
    student = get_or_create_student(request.user)
    payments = Payment.objects.filter(student=student).order_by('-payment_date')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        # In a real implementation, you would integrate with a payment gateway
        transaction_id = f"TXN{''.join(random.choices(string.ascii_uppercase + string.digits, k=12))}"
        
        Payment.objects.create(
            student=student,
            amount=amount,
            transaction_id=transaction_id
        )
        
        student.wallet_balance += float(amount)
        student.save()
        
        return redirect('wallet')
    
    return render(request, 'wallet.html', {
        'student': student,
        'payments': payments
    })

# core/views.py - Update the staff_dashboard function
@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    laundry_bags = LaundryBag.objects.all().order_by('-request_date')
    lost_items = LostItem.objects.filter(is_claimed=False)
    
    # Calculate counts for different statuses
    total_bags = laundry_bags.count()
    pending_pickup = laundry_bags.filter(status='requested').count()
    ready_for_delivery = laundry_bags.filter(status='ready').count()
    total_lost_items = lost_items.count()
    
    if request.method == 'POST' and 'update_status' in request.POST:
        bag_id = request.POST.get('bag_id')
        new_status = request.POST.get('status')
        
        bag = get_object_or_404(LaundryBag, id=bag_id)
        bag.status = new_status
        
        if new_status == 'picked_up':
            bag.pickup_date = timezone.now()
        elif new_status == 'ready':
            bag.ready_date = timezone.now()
        elif new_status == 'delivered':
            bag.delivery_date = timezone.now()
        
        bag.save()
        
        # Create notification for student
        Notification.objects.create(
            user=bag.student.user,
            title="Laundry Status Updated",
            message=f"Your laundry bag {bag.qr_code} is now {bag.get_status_display()}"
        )
        
        return redirect('staff_dashboard')
    
    return render(request, 'staff_dashboard.html', {
        'laundry_bags': laundry_bags,
        'lost_items': lost_items,
        'total_bags': total_bags,
        'pending_pickup': pending_pickup,
        'ready_for_delivery': ready_for_delivery,
        'total_lost_items': total_lost_items,
    })