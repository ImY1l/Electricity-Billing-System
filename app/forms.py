"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email, RegexValidator
from django.core.exceptions import ValidationError
from .models import Meter, Customer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import PasswordResetForm

User = get_user_model()

### --------- Authentication Form (Login) --------- ###
class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    uusername_or_email = forms.CharField(label="Username or Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get("username_or_email")
        password = cleaned_data.get("password")

        if username_or_email and password:
            # Try to authenticate using the username
            user = authenticate(username=username_or_email, password=password)
            if user is None:
                # If authentication fails, try using the email
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user = User.objects.get(email=username_or_email)
                    user = authenticate(username=user.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is None:
                raise forms.ValidationError("Invalid username/email or password.")

            cleaned_data["user"] = user
        return cleaned_data
    

### --------- Step 1: Meter ID Validation Form --------- ###
class MeterVerificationForm(forms.Form):
    """Form to check if a meter ID exists and is not registered."""
    meter_id = forms.CharField(
        label="Meter ID",
        max_length=6,
        validators=[RegexValidator(regex=r'^M\d{5}$', message="Meter ID must be in the format MXXXXX.")],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Meter ID (e.g., M12345)'})
    )

    def clean_meter_id(self):
        meter_id = self.cleaned_data['meter_id'].strip().upper()

        try:
            meter = Meter.objects.get(meter_id=meter_id)
            if meter.customer:
                raise ValidationError("This meter is already registered.")
            return meter_id
        except Meter.DoesNotExist:
            raise ValidationError("Invalid Meter ID. Please check and try again.")



### --------- Step 2: Customer Registration Form --------- ###
class CustomerRegistrationForm(forms.ModelForm):
    """Registration form for new customers."""
    username = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^[a-zA-Z0-9_]+$', 'Username can only contain letters, numbers, and underscores.')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )
    customer_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'})
    )
    customer_email = forms.EmailField(
        validators=[validate_email],
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'})
    )
    customer_number = forms.CharField(
        max_length=13,
        validators=[RegexValidator(r'^\+?\d{10,13}$', 'Enter a valid phone number.')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'})
    )
    customer_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter address', 'rows': 3})
    )
    meter_id = forms.CharField(widget=forms.HiddenInput(), required=False)  # Ensure it's not required

    class Meta:
        model = Customer
        fields = ['customer_name', 'customer_email', 'customer_number', 'customer_address']

    def clean_username(self):
        username = self.cleaned_data['username'].strip().lower()
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_customer_email(self):
        email = self.cleaned_data['customer_email'].strip().lower()
        if Customer.objects.filter(customer_email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        return cleaned_data


User = get_user_model()

class ResetPasswordForm(PasswordResetForm):
    """Custom password reset form to ensure the email exists in the system."""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No account found with this email.")
        return email



### --------- Password Change Form --------- ###
class PasswordChangeForm(forms.Form):
    """Form for changing passwords."""
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Old Password")
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirm New Password")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise ValidationError("New passwords do not match.")

        return cleaned_data

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['customer_name', 'customer_email', 'customer_number', 'customer_address']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'customer_number': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
