"""
Definition of models.
"""

from django.db import models

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from enum import Enum


class User(AbstractUser):
    ROLE_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('SUPPORT_ADMIN', 'Support Admin'),
        ('STAFF', 'Staff'),
        ('UTILITY_PROVIDER', 'Utility Provider'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    phone_number = models.CharField(max_length=13, blank=True, null=True)
    address = models.CharField(max_length=120, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    def assign_role(self, role_name):
        group, created = Group.objects.get_or_create(name=role_name)
        self.groups.add(group)
        self.save()

class BaseProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="%(class)s_profile")
    identifier = models.CharField(max_length=6, unique=True, null=True, blank=True)


    PREFIX = ""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.identifier:
            count = self.__class__.objects.count() + 1
            self.identifier = f"{self.PREFIX}{count:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.user.username}"

class Customer(BaseProfile):
    PREFIX = "C"
    

class UtilityProvider(BaseProfile):
    PREFIX = "U"

class SupportAdmin(BaseProfile):
    PREFIX = "A"

class Staff(BaseProfile):
    PREFIX = "S"



class Customer(models.Model):
    # Define the fields in the model
    customer_id = models.CharField(max_length=6, primary_key=True)  # Ensure it's CharField
    meter_id = models.CharField(max_length=100)  # Assuming meter_id is a string
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_number = models.CharField(max_length=15)  # For phone numbers
    customer_address = models.TextField()
    date_joined = models.DateField(default=now)

    def __str__(self):
        return self.customer_name

class Item(models.Model):
    item_id = models.CharField(primary_key=True, max_length=10)
    item_name = models.TextField()
    item_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Item {self.item_id}: {self.item_name}"


class Meter(models.Model):
    meter_id = models.CharField(
        primary_key=True,
        max_length=6,
        validators=[RegexValidator(regex=r'^M\d{5}$', message="Meter ID must be in the format MXXXXX.")]
    )
    meter_reading = models.IntegerField()
    tariff_rate = models.DecimalField(max_digits=10, decimal_places=2)
    customer = models.OneToOneField(Customer, on_delete=models.SET_NULL, null=True, related_name="meter")

    def __str__(self):
        return f"Meter {self.meter_id}"
    class Meta:
        unique_together = ['meter_id', 'customer']


class Bill(models.Model):
    STATUS_CHOICES = [
        (True, 'Paid'),
        (False, 'Unpaid')
    ]
    bill_id = models.CharField(primary_key=True, max_length=6)
    # Ensure the customer_id matches the type of the primary key in Customer
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(choices=STATUS_CHOICES)
    creation_date = models.DateField()
    penalty_fee = models.DecimalField(max_digits=10, decimal_places=2)
    usage =  models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Bill {self.bill_id}"


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('fpx', 'FPX Online Banking'),
        ('tng', 'Touch \'n Go eWallet'),
    ]
    payment_id = models.CharField(primary_key=True, max_length=6)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment {self.payment_id}"


class Issue(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('solved', 'Solved'),
    ]
    issue_id = models.CharField(primary_key=True, max_length=6)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    title = models.CharField(max_length=15)
    description = models.CharField(max_length=300)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    ticket_id = models.CharField(max_length=6, unique=True)

    def __str__(self):
        return f"Issue {self.issue_id}"


class Feedback(models.Model):
    feedback_id = models.CharField(primary_key=True, max_length=6)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.CharField(max_length=200)
    feedback_date = models.DateField()

    def __str__(self):
        return f"Feedback {self.feedback_id}"
    


class UsageMetrics(models.Model):
    total_customers = models.IntegerField()
    total_bills = models.IntegerField()
    total_usage = models.FloatField()
    avg_usage = models.FloatField()

    class Meta:
        managed = False  
        db_table = "UsageMetrics"  

class Tariff(models.Model):
    CATEGORY_CHOICES = [
        (1, "For the first 200 kWh (1 - 200 kWh) per month"),
        (2, "For the next 100 kWh (201 - 300 kWh) per month"),
        (3, "For the next 300 kWh (301 - 600 kWh) per month"),
        (4, "For the next 300 kWh (601 - 900 kWh) per month"),
        (5, "For the next kWh (901 kWh onwards) per month"),
    ]
    
    category = models.IntegerField(choices=CATEGORY_CHOICES, unique=True)
    unit = models.CharField(max_length=10, default="sen/kWh")
    rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.get_category_display()} - {self.rate}"
    
class ScheduledBilling(models.Model):
    schedule_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scheduled Billing on {self.schedule_date}"