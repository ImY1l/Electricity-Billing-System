"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from app import views, forms
import django.contrib.auth.views
from django.contrib.auth.views import LoginView, LogoutView
from datetime import datetime
admin.autodiscover()
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from app.views import change_password
from app.views import validate_meter, registration_step_2
from app.forms import ResetPasswordForm

urlpatterns = [
    # Home route
    path('', views.home, name='home'),
    
   # Admin route
    path('admin/', admin.site.urls),
    
    # Static pages
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),

    # Authentication views
    path('login/', LoginView.as_view(template_name='app/login.html'), name='login'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('menu/', views.menu, name='menu'),
    path('role-redirect/', views.role_based_redirect, name='role_redirect'),
    path('register/', validate_meter, name='validate_meter'),
    path('register/step2/', registration_step_2, name='register_step_2'),

    # Customer URLs
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/bills/', views.bills, name='bills'),
    path('customer/make-payment/<str:bill_id>', views.make_payment, name='make_payment'),
    path('customer/payment_receipt/<str:bill_id>/', views.payment_receipt, name='payment_receipt'),
    path('customer/submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('customer/submit-issue/', views.submit_issue, name='submit_issue'),


    # Support Admin URLs
    path('support-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('support-admin/view-bills/', views.view_bills, name='view_bills_admin'),
    path('support-admin/bill-details/<str:bill_id>/', views.bill_details, name='bill_details'),
    path('support-admin/issues/', views.customer_issues, name='customer_issues'),
    path('support-admin/issues/<str:issue_id>/', views.issue_details, name='issue_details'),
    path('support-admin/update-issue-status/<str:issue_id>/', views.update_issue_status, name='update_issue_status'),
    path('support-admin/view-feedback/', views.view_feedback, name='view_feedback_admin'),
    path('admin/', admin.site.urls),
    

    # Staff URLs
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/manage-customer-accounts/', views.manage_customer_accounts, name='manage_customer_accounts'),
    path('staff/track-overdue-bills/', views.track_overdue_bills, name='track_overdue_bills'),
    path('staff/usage-monitoring/', views.usage_monitoring, name='usage_monitoring'),
    path('view-customer/<str:customer_id>/', views.staff_viewCustomer, name='staff_viewCustomer'),
    path('update-customer/<str:customer_id>/', views.staff_updateCustomer, name='staff_updateCustomer'),
    path('staff/view-bill/<str:bill_id>/', views.staff_viewBill, name='staff_viewBill'),
    path('staff/set-due-date/<str:bill_id>/', views.staff_setDueDate, name='staff_setDueDate'),
    


    # utility provider URLs
    path("utility-dashboard/", views.utility_dashboard, name="utility_dashboard"),
    path('meter-readings/', views.meter_readings, name='meter_readings'),
    path("update-tariff/", views.update_tariff, name="update_tariff"),
    path("update-tariff/<int:category>/", views.update_tariff, name="update_tariff_category"),
    path('overdue-bills/', views.overdue_bills, name='overdue_bills'),
    path('account-details/<str:bill_id>/', views.account_details, name='account_details'),
    path('set-penalty/<str:bill_id>/', views.set_penalty, name='set_penalty'),
    path("schedule-monthly-bills/", views.schedule_monthly_bills, name="schedule_monthly_bills"),

    # Password management views
   path(
        'change_password/', 
        auth_views.PasswordChangeView.as_view(
            template_name='app/change_password.html', 
            success_url='/change-password-done/'
        ), 
        name='change_password'
    ),
    path(
        'change-password-done/', 
        auth_views.PasswordChangeDoneView.as_view(
            template_name='app/change_password_done.html'
        ), 
        name='password_change_done'
    ),


    # Password Reset URLs
        path(
        'reset-password/', 
        auth_views.PasswordResetView.as_view(
            template_name='app/reset_password_form.html',
            form_class=ResetPasswordForm
        ), 
        name='password_reset'
    ),
    path(
        'reset-password/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='app/reset_password_done.html'
        ), 
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='app/reset_password_confirm.html'
        ), 
        name='password_reset_confirm'
    ),
    path(
        'reset/complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='app/reset_password_complete.html'
        ), 
        name='password_reset_complete'
    ),
    


]
