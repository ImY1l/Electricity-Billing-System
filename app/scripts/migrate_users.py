from app.models import Customer, User
from django.contrib.auth.hashers import make_password

def run():
    for customer in Customer.objects.all():
        User.objects.create(
            username=customer.username,
            password=make_password(customer.password),  # Secure password storage
            role="CUSTOMER",
            email=customer.customer_email,
            phone_number=customer.customer_phone,
            address=customer.customer_address,
        )
    print("Customer migration completed.")
