# core/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('request-pickup/', views.request_laundry_pickup, name='request_pickup'),
    path('track-laundry/', views.track_laundry, name='track_laundry'),
    path('lost-found/', views.lost_found, name='lost_found'),
    path('search-lost-items/', views.search_lost_items, name='search_lost_items'),
    path('claim-item/<int:item_id>/', views.claim_item, name='claim_item'),
    path('wallet/', views.wallet, name='wallet'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
]