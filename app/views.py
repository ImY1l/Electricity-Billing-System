import random
from sqlite3 import IntegrityError
from django.shortcuts import render, redirect

# Create your views here.
from django.http import Http404, HttpRequest # type: ignore
from django.template import RequestContext # type: ignore ##--
from datetime import datetime, date, timedelta
from django.utils import timezone

from django.contrib import messages
from django.shortcuts import  get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login as auth_login
from .forms import BootstrapAuthenticationForm
from .forms import CustomerForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from django.utils import timezone
from .forms import MeterVerificationForm, CustomerRegistrationForm
from .forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordChangeForm
from django.db import connection

from .models import (
    Customer, User, Bill, Payment, 
    Issue, Feedback, SupportAdmin,
    UtilityProvider, Staff, Meter, UsageMetrics,
    ScheduledBilling, Tariff
)

from .forms import ResetPasswordForm

# Session keys
CUSTOMER_SESSION_KEY = 'customer_id'
ADMIN_SESSION_KEY = 'admin_id'
STAFF_SESSION_KEY = 'staff_id'
UTILITY_SESSION_KEY = 'utility_id'

# ========================
# Common Helper Functions
# ========================
def get_current_user(request):
    """Returns the logged-in user based on session"""
    if CUSTOMER_SESSION_KEY in request.session:
        return Customer.objects.get(customer_id=request.session[CUSTOMER_SESSION_KEY])
    if ADMIN_SESSION_KEY in request.session:
        return SupportAdmin.objects.get(admin_id=request.session[ADMIN_SESSION_KEY])
    if STAFF_SESSION_KEY in request.session:
        return Staff.objects.get(staff_id=request.session[STAFF_SESSION_KEY])
    if UTILITY_SESSION_KEY in request.session:
        return UtilityProvider.objects.get(utility_id=request.session[UTILITY_SESSION_KEY])
    return None

def role_based_redirect(request):
    if request.user.is_authenticated:
        role = request.user.role.upper()  # Use .upper() if roles are stored in uppercase
        if role == 'CUSTOMER':
            return redirect('customer_dashboard')
        elif role == 'SUPPORT_ADMIN':
            return redirect('admin_dashboard')
        elif role == 'STAFF':
            return redirect('staff_dashboard')
        elif role == 'UTILITY_PROVIDER':
            return redirect('utility_dashboard')
    
    # Redirect to home if no valid role or not authenticated
    return redirect('home')


def migrate_users():
    for customer in Customer.objects.all():
        User.objects.create(
            username=customer.username,
            password=customer.password,  # Store securely in production!
            role="CUSTOMER",
            email=customer.customer_email,
            phone_number=customer.customer_phone,
            address=customer.customer_address,
        )

    for staff in Staff.objects.all():
        User.objects.create(
            username=staff.username,
            password=staff.password,
            role="STAFF",
            email=staff.staff_email,
            phone_number=staff.staff_phone,
        )

    for admin in SupportAdmin.objects.all():
        User.objects.create(
            username=admin.username,
            password=admin.password,
            role="ADMIN",
            email=admin.admin_email,
            phone_number=admin.admin_phone,
        )

    for provider in UtilityProvider.objects.all():
        User.objects.create(
            username=provider.username,
            password=provider.password,
            role="UTILITY_PROVIDER",
            email=provider.up_email,
            phone_number=provider.up_phone,
        )
    print("User migration completed.")

# ========================
# Authentication Views
# ========================
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                # Log the user in
                auth_login(request, user)

                # Role-based redirection
                if user.role == 'CUSTOMER':
                    return redirect('customer_dashboard')
                elif user.role == 'UTILITY_PROVIDER':
                    return redirect('utility_dashboard')
                elif user.role == 'SUPPORT_ADMIN':
                    return redirect('admin_dashboard')
                elif user.role == 'STAFF':
                    return redirect('staff_dashboard')
                else:
                    return HttpResponse('Invalid role', status=403)
            else:
                return HttpResponse('Invalid username or password', status=401)
        else:
            return HttpResponse('Invalid form data', status=400)

    # Render the login form for GET requests
    form = AuthenticationForm()
    return render(request, 'app/login.html', {'form': form})


def logout(request):
    if request.method == "GET":
        logout(request)
        return redirect('home')






def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    
    # Render the same page regardless of login status
    return render(
        request,
        'app/index.html',
        {
            'title': 'Home Page',
            'year': datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'Electricity Billing System',
            'message':'This application processes ...',
            'year':datetime.now().year,
        }
    )


# ========================
# Menu View
# ========================
@login_required
def menu(request):
    user = get_current_user(request)
    if not user:
        return redirect('login')
    
    context = {
        'title': 'Main Menu',
        'is_customer': isinstance(user, Customer),
        'is_support_admin': isinstance(user, SupportAdmin),
        'is_staff': isinstance(user, Staff),
        'is_utility': isinstance(user, UtilityProvider),
        'user': user,
        'year': datetime.now().year,
    }
    return render(request, 'app/menu.html', context)

'''def registration(request):
    """
    Step 1: Validate meter ID and initiate registration process.
    """
    if request.method == 'POST':
        meter_id = request.POST.get('meter_id')
        
        # Validate Meter ID
        try:
            # Check if meter ID exists and is not already assigned to a customer
            meter = Meter.objects.get(meter_id=meter_id)
            if hasattr(meter, 'customer'):
                return render(request, 'app/registration_1.html', {
                    'error': 'This meter is already registered to a customer.'
                })
            
            # Store meter ID in session for step 2
            request.session['meter_id'] = meter_id
            return redirect('registration_step2')
        
        except Meter.DoesNotExist:
            return render(request, 'app/registration_1.html', {
                'error': 'Invalid meter ID. Please check and try again.'
            })
    
    return render(request, 'app/registration_1.html')'''

def validate_meter(request):
    if request.method == "POST":
        form = MeterVerificationForm(request.POST)
        if form.is_valid():
            request.session['meter_id'] = form.cleaned_data['meter_id']  # Store meter ID in session
            return redirect('register_step_2')  # Redirect to step 2
    else:
        form = MeterVerificationForm()
    
    return render(request, 'app/registration_1.html', {'form': form})




def registration_step_2(request):
    meter_id = request.session.get('meter_id')  # Get meter ID from session
    if not meter_id:
        return redirect('validate_meter')  # Redirect back if no meter ID found

    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            # Generate a customer_id (e.g., C00001)
            customer_id = f"C{random.randint(10000, 99999)}"

            try:
                # Create the User object
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                    email=form.cleaned_data['customer_email'],
                    role='CUSTOMER'
                )
            except IntegrityError:
                form.add_error('username', "Username already exists. Please choose a different username.")
                return render(request, 'app/registration_2.html', {'form': form, 'meter_id': meter_id})

            # Try to fetch the meter using meter_id from session
            try:
                meter = Meter.objects.get(meter_id=meter_id)
            except Meter.DoesNotExist:
                form.add_error(None, "Invalid Meter ID. Please start over.")
                return render(request, 'app/registration_2.html', {'form': form, 'meter_id': meter_id})

            try:
                # Create Customer object and save it
                customer = Customer.objects.create(
                    customer_id=customer_id,  # Generated customer_id
                    meter_id=meter.meter_id,
                    customer_name=form.cleaned_data['customer_name'],
                    customer_address=form.cleaned_data['customer_address'],
                    customer_number=form.cleaned_data['customer_number'],
                    customer_email=form.cleaned_data['customer_email']
                )
            except IntegrityError as e:
                # Handle any integrity errors
                form.add_error(None, "Error creating customer. Please try again.")
                return render(request, 'app/registration_2.html', {'form': form, 'meter_id': meter_id})

            # Link the meter to the newly created customer
            meter.customer = customer
            meter.save()

            # Successfully created, now redirect to login
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')

    else:
        form = CustomerRegistrationForm()

    return render(request, 'app/registration_2.html', {'form': form, 'meter_id': meter_id})


User = get_user_model()  # Get custom User model

def reset_password(request):
    """
    Handle password reset requests.
    """
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)  # Look up the user in the User model
                
                # TODO: Implement password reset email logic

                return redirect('password_reset_sent')  # Redirect to a success page
            except User.DoesNotExist:
                form.add_error('email', 'No account found with this email address.')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'app/reset_password.html', {'form': form})


def password_reset_sent(request):
    """Display confirmation page after password reset request."""
    return render(request, 'app/password_reset_sent.html')


# ----------------------------------------------
# Customer Dashboard Views
# ----------------------------------------------
def is_customer(user):
    return user.is_authenticated and user.role == 'CUSTOMER'


@login_required
@user_passes_test(is_customer)
def customer_dashboard(request):
     # Fetch the customer associated with the logged-in user
    customer_profile = get_object_or_404(Customer, customer_email=request.user.email)

    # Retrieve the bills for this customer
    bills = Bill.objects.filter(customer=customer_profile).order_by('-due_date')

    # If no bills found, you can add a message or handle as needed
    if not bills:
        messages.info(request, "No bills found for your account.")

    # Pass both customer profile and bills to the template
    return render(request, 'app/customer_dashboard.html', {'customer': customer_profile, 'bills': bills})



@login_required
@user_passes_test(is_customer)
def bills(request): 
    """Retrieve and display bills for the logged-in customer."""
    try:
        customer = get_object_or_404(Customer, customer_email=request.user.email)
    except Http404:
        return redirect('customer_dashboard')  

    bills = Bill.objects.filter(customer=customer).order_by('-due_date')  # Order by due date
    return render(request, 'app/bills.html', {'bills': bills})

@login_required
def make_payment(request, bill_id):
    """Handles making a payment for a specific bill."""
    customer = get_object_or_404(Customer, customer_email=request.user.email)
    bill = get_object_or_404(Bill, bill_id=bill_id, customer=customer)  # Ensure customer owns the bill

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

         # Generate a truly unique PXXXXX ID
        while True:
            random_number = random.randint(10000, 99999)  # Generate a 5-digit number
            new_payment_id = f'P{random_number}'
            if not Payment.objects.filter(payment_id=new_payment_id).exists():
                break  # Ensure uniqueness before using

        # Create Payment
        Payment.objects.create(
            payment_id=new_payment_id,
            customer=customer,
            bill=bill,  # Link payment to bill
            payment_date=datetime.now().date(),
            payment_method=payment_method,
            amount=bill.amount
        )

        # Mark bill as paid
        bill.paid = True
        bill.save()

        return redirect('payment_receipt', bill_id=bill.bill_id)

    return render(request, 'app/makePayment.html', {'bill': bill})



@login_required
def payment_receipt(request, bill_id):
    """Displays the payment receipt for a paid bill."""
    customer = get_object_or_404(Customer, user=request.user)
    bill = get_object_or_404(Bill, bill_id=bill_id, customer=customer)
    payment = get_object_or_404(Payment, bill=bill)  # Get the related payment

    return render(request, 'app/payment_receipt.html', {'payment': payment})

@login_required
def submit_feedback(request):
    """Allow customers to submit feedback with a rating and optional comments."""
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comments = request.POST.get('comments', '').strip()  # Default empty string, remove leading/trailing spaces

        # Ensure rating is an integer and within valid range
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Invalid rating value")
        except ValueError:
            messages.error(request, "Invalid rating. Please select a number between 1 and 5.")
            return redirect('submit_feedback')

        # Get the customer linked to the logged-in user
        customer = get_object_or_404(Customer, customer_email=request.user.email)

        # Generate a unique feedback_id in "FXXXXX" format
        while True:
            last_feedback = Feedback.objects.order_by('-feedback_id').first()
            last_id = int(last_feedback.feedback_id[1:]) if last_feedback else 0
            new_feedback_id = f"F{last_id + 1:05}"  # Generate a new ID

            # Check if feedback_id already exists to ensure uniqueness
            if not Feedback.objects.filter(feedback_id=new_feedback_id).exists():
                break  # Exit loop if the ID is unique

        # Save feedback with "No comments provided" if empty
        Feedback.objects.create(
            feedback_id=new_feedback_id,
            customer=customer,
            rating=rating,
            comment=comments if comments else "No comments provided",
            feedback_date=timezone.now().date()
        )

        messages.success(request, "Thank you for your feedback!")
        return redirect('customer_dashboard')

    return render(request, 'app/submitFeedback.html')


@login_required
def submit_issue(request):
    """Allow customers to submit an issue."""
    if request.method == 'POST':
        title = request.POST.get('issue_title', '').strip()
        description = request.POST.get('issue_description', '').strip()

        # Ensure title and description are provided
        if not title or not description:
            messages.error(request, "Title and description are required.")
            return redirect('submit_issue')

        # Get the logged-in customer's profile
        customer = get_object_or_404(Customer, customer_email=request.user.email)

        # Generate a unique random issue_id (IXXXXX)
        while True:
            new_issue_id = f"I{random.randint(10000, 99999)}"
            if not Issue.objects.filter(issue_id=new_issue_id).exists():
                break

        # Generate a unique random ticket_id (TXXXXX)
        while True:
            new_ticket_id = f"T{random.randint(10000, 99999)}"
            if not Issue.objects.filter(ticket_id=new_ticket_id).exists():
                break

        # Save the issue with default status "Open"
        Issue.objects.create(
            issue_id=new_issue_id,
            customer=customer,
            title=title,
            description=description,
            status="open",  # Default status
            ticket_id=new_ticket_id
        )

        messages.success(request, "Issue submitted successfully.")
        return redirect('customer_dashboard')

    return render(request, 'app/submitIssue.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']

            # Verify old password
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)  # Keep the user logged in
                return redirect('customer_dashboard')  # Redirect to dashboard
            else:
                form.add_error('old_password', 'Incorrect old password.')
    else:
        form = PasswordChangeForm()

    return render(request, 'app/change_password.html', {'form': form})





# Check if user is support admin
def is_support_admin(user):
    return user.is_authenticated and user.role == 'SUPPORT_ADMIN'

@login_required
@user_passes_test(is_support_admin)
def admin_dashboard(request):
    try:
        # Get the support admin profile of the logged-in user
        admin_profile = SupportAdmin.objects.get(user=request.user)
    except SupportAdmin.DoesNotExist:
        messages.error(request, "Admin profile does not exist.")
        return redirect('home')  # Or redirect to an appropriate page

    # Pass the admin profile to the template
    return render(request, 'app/admin_dashboard.html', {'customer': admin_profile})


@login_required
@user_passes_test(is_support_admin)
def view_bills(request):
    query = request.GET.get('search', '')  # Get search query from URL
    bills = Bill.objects.all().order_by('-due_date')

    if query:
        bills = bills.filter(bill_id__icontains=query)  # Filter bills by ID

    if not bills.exists():
        messages.info(request, "No bills available at the moment.")
    
    return render(request, 'app/admin_viewBill.html', {'bills': bills, 'search_query': query})



@login_required
@user_passes_test(is_support_admin)
def bill_details(request, bill_id):
    try:
        bill = get_object_or_404(Bill, bill_id=bill_id)
        messages.info(request, f"Viewing details for Bill ID: {bill_id}")
    except Exception as e:
        messages.error(request, f"Failed to retrieve bill details: {str(e)}")
        return redirect('view_bills')
        
    return render(request, 'app/admin_billDetails.html', {'bill': bill})


@login_required
def customer_issues(request):
    issues = Issue.objects.all()

    if not issues.exists():
        messages.info(request, "No customer issues have been reported yet.")
    return render(request, 'app/admin_viewIssue.html', {'issues': issues})

@login_required
def issue_details(request, issue_id):
    issue = get_object_or_404(Issue, issue_id=issue_id)  
    return render(request, 'app/issue_details.html', {'issue': issue})


@login_required
def update_issue_status(request, issue_id):
    issue = get_object_or_404(Issue, issue_id=issue_id)  
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        admin_comment = request.POST.get('admin_comment', '').strip()

        if new_status:  # Ensure status is provided
            issue.status = new_status
            issue.save()
            messages.success(request, f"Issue ID {issue.issue_id} status updated to {issue.status}.")
        else:
            messages.error(request, "Invalid status provided.")

        return redirect('update_issue_status', issue_id=issue.issue_id)

    
    return render(request, 'app/update_issue.html', {'issue': issue})


@login_required
@user_passes_test(is_support_admin)
def view_feedback(request):
    feedbacks = Feedback.objects.all().order_by('-feedback_date')

    # Get filter parameter
    rating_filter = request.GET.get('rating', 'all')

    # Apply rating filter
    if rating_filter:
        if rating_filter == 'positive':
            feedbacks = feedbacks.filter(rating__gte=4)
        elif rating_filter == 'neutral':
            feedbacks = feedbacks.filter(rating=3)
        elif rating_filter == 'negative':
            feedbacks = feedbacks.filter(rating__lte=2)

    return render(request, 'app/admin_viewFeedback.html', {
        'feedbacks': feedbacks,
        'rating_filter': rating_filter,
    })

# ========================
# Staff Views
# ========================
def is_staff(user):
    return user.is_authenticated and user.role == 'STAFF'

@login_required
@user_passes_test(is_staff)
def staff_dashboard(request):
    try:
        # Get the staff profile of the logged-in user
        staff_profile = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        messages.error(request, "Staff profile does not exist.")
        return redirect('home')  # Or redirect to a different page, like registration

    # Pass the customer profile to the template
    return render(request, 'app/staff_dashboard.html', {'customer': staff_profile})

@login_required
@user_passes_test(is_staff)
def manage_customer_accounts(request):
    customers = Customer.objects.all()
    return render(request, 'app/manage_customer_accounts.html', {'customers': customers})

@login_required
@user_passes_test(is_staff)
def staff_viewCustomer(request, customer_id):
    customer = get_object_or_404(Customer, customer_id=customer_id)
    bills = Bill.objects.filter(customer=customer)  # Fetch bills for this customer

    return render(request, 'app/staff_viewCustomer.html', {'customer': customer, 'bills': bills})


@login_required
@user_passes_test(is_staff)
def staff_updateCustomer(request, customer_id):
    customer = get_object_or_404(Customer, customer_id=customer_id)  # Fetch customer

    if request.method == 'POST':  # Handle form submission
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer details updated successfully!")
            return redirect('staff_updateCustomer', customer_id=customer.customer_id)  # Redirect to the same page
    else:
        form = CustomerForm(instance=customer)  # Pre-fill form with existing data

    return render(request, 'app/staff_updateCustomer.html', {'form': form, 'customer': customer})


@login_required
@user_passes_test(is_staff)
def staff_viewBill(request, bill_id):
    bill = get_object_or_404(Bill, bill_id=bill_id)
    return render(request, 'app/staff_viewBill.html', {'bill': bill})

@login_required
@user_passes_test(is_staff)
def staff_setDueDate(request, bill_id):
    # Fetch the bill by its bill_id
    bill = get_object_or_404(Bill, bill_id=bill_id)

    if request.method == 'POST':
        # Get the due date from the form
        due_date = request.POST.get('due_date')

        # Update the due date of the bill
        bill.due_date = due_date
        bill.save()

        # Add success message
        messages.success(request, f"Due date for Bill {bill.bill_id} has been successfully updated!")


    # Render the template with the bill data
    return render(request, 'app/staff_setDueDate.html', {'bill': bill})


@login_required
@user_passes_test(is_staff)
def track_overdue_bills(request):
    today = date.today()
    overdue_bills = Bill.objects.filter(due_date__lt=today, paid=False)

    if not overdue_bills.exists():  # Use .exists() instead of checking `if not overdue_bills`
        message = "No overdue bills found"
    else:
        message = None
    
    return render(request, 'app/track_overdue_bills.html', {'overdue_bills': overdue_bills, 'message': message})

@login_required
@user_passes_test(is_staff)
def usage_monitoring(request):
    # Get the selected month and year from the request
    selected_month = request.GET.get('month', None)
    
    # Initialize usagemetrics as None
    usagemetrics = None

    # Only query the database if a month and year are selected
    if selected_month:
        # Query the UsageMetrics view with the selected month and year
        usagemetrics = UsageMetrics.objects.raw(f"""
            SELECT 
                (SELECT COUNT(*) 
                 FROM app_customer 
                 WHERE strftime('%Y-%m', date_joined) <= '{selected_month}') AS total_customers,

                (SELECT COUNT(*) 
                 FROM app_bill 
                 WHERE strftime('%Y-%m', creation_date) <= '{selected_month}') AS total_bills,

                (SELECT SUM(usage) 
                 FROM app_bill 
                 WHERE strftime('%Y-%m', creation_date) <= '{selected_month}') AS total_usage,

                (SELECT AVG(usage) 
                 FROM app_bill 
                 WHERE strftime('%Y-%m', creation_date) <= '{selected_month}') AS avg_usage,

                1 AS id
        """)[0]  # Get the first (and only) record

    context = {
        'usagemetrics': usagemetrics,  # Will be None if no month is selected
        'selected_month': selected_month,
    }

    return render(request, 'app/usage_monitoring.html', context)

@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    if created and instance.is_staff:  # Ensure only staff users get a profile
        Staff.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_staff_profile(sender, instance, **kwargs):
    if hasattr(instance, 'staff_profile'):
        instance.staff_profile.save()

# ========================
# Utility Provider Views
# ========================
def utility_dashboard(request):
    overdue_count = Bill.objects.filter(paid=False, due_date__lt=timezone.now()).count()
    total_customers = Meter.objects.count()
    #latest_tariff = Tariff.objects.latest('updated_at')

    context = {
        'overdue_count': overdue_count,
        'total_customers': total_customers,
        #'latest_tariff': latest_tariff,
    }
    return render(request, 'app/utility_dashboard.html', context)

def meter_readings(request):
    tariffs = Tariff.objects.all() 
    return render(request, "app/meter_readings.html", {"tariffs": tariffs})

@login_required
def update_tariff(request, category=None):
    if request.method == "POST":
        category = request.POST.get("category")
        new_rate = request.POST.get("new_rate")

        if not category or not new_rate:
            messages.error(request, "All fields are required.")
            return redirect("meter_readings")

        try:
            category = int(category)
            new_rate = float(new_rate)

            if new_rate < 1 or new_rate > 100:
                messages.error(request, "Invalid input. Please enter a valid tariff value.")
                return redirect("meter_readings")

            tariff = get_object_or_404(Tariff, category=category)
            tariff.rate = new_rate
            tariff.save()

            messages.success(request, f"Tariff for category {category} updated successfully!")

        except ValueError:
            messages.error(request, "Invalid input. Please enter a valid number.")

    return redirect("meter_readings")

@login_required
def overdue_bills(request):
    overdue_bills = Bill.objects.filter(paid=False, due_date__lt=timezone.now()).select_related('customer')
    return render(request, 'app/overdue_bills.html', {'overdue_bills': overdue_bills})

def account_details(request, bill_id):
    bill = get_object_or_404(Bill, bill_id=bill_id)
    customer = get_object_or_404(Customer, customer_id=bill.customer.customer_id)
    return render(request, 'app/account_details.html', {'bill': bill})

def set_penalty(request, bill_id):
    bill = get_object_or_404(Bill, bill_id=bill_id)
    if request.method == 'POST':
        penalty_amount = request.POST.get('penalty_amount')
        if 200 <= float(penalty_amount) <= 500:
            bill.penalty_fee = penalty_amount
            bill.save()
            return redirect('overdue_bills')
        else:
            return render(request, 'app/set_penalty.html', {'bill': bill, 'error': "Penalty must be between RM 200 and RM 500"})
    return render(request, 'app/set_penalty.html', {'bill': bill})

@login_required
def schedule_monthly_bills(request):
    error_message = None

    if request.method == 'POST':
        date_str = request.POST.get('schedule_date')

        if not date_str:
            error_message = 'Invalid date.'
        else:
            try:
                schedule_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                today = timezone.now().date()
                max_date = today + timedelta(days=30)

                if schedule_date <= today or schedule_date > max_date or schedule_date.year != today.year:
                    error_message = 'Invalid date.'
                else:
                    ScheduledBilling.objects.create(schedule_date=schedule_date)
                    return render(request, 'app/schedule_success.html', {'schedule_date': schedule_date})

            except ValueError:
                error_message = 'Invalid date.'

    return render(request, 'app/schedule_monthly_bills.html', {'error_message': error_message})

@login_required
def bill_generation_success(request):
    return render(request, 'app/bill_generation_success.html')


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'CUSTOMER':
        Customer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    if instance.role == 'CUSTOMER':
        instance.customer_profile.save()
