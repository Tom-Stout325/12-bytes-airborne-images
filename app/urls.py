from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from .views import *

urlpatterns = [


    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    path('', login_required(TemplateView.as_view(template_name='home.html')), name='home'),
    path('home/', login_required(TemplateView.as_view(template_name='home.html')), name='home'),


    path('home/', login_required(TemplateView.as_view(template_name='home.html')), name='home'),
    # path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('profile/', pilot_profile, name='pilot_profile'),

    path('profile/edit/', edit_pilot_profile, name='edit_pilot_profile'),
    path('profile/delete/', delete_pilot_profile, name='delete_pilot_profile'),

    path('profile/training/add/', add_training_record, name='add_training_record'),
    path('profile/training/edit/<int:pk>/', edit_training_record, name='edit_training_record'),
    path('profile/training/delete/<int:pk>/', delete_training_record, name='delete_training_record'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]