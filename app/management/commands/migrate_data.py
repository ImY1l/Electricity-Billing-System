from django.core.management.base import BaseCommand
from app.models import User, Customer, UtilityProvider, SupportAdmin, Staff

class Command(BaseCommand):
    help = "Migrate data from old tables to the new User model"

    def handle(self, *args, **kwargs):
        # Migrate Customer Data
        for customer in Customer.objects.all():
            user = User.objects.create_user(
                username=f"customer_{customer.customer_id}",
                password="default_password",
                email=customer.email,
                phone_number=customer.phone,
                address=customer.address,
                role='CUSTOMER'
            )
            print(f"Customer migrated: {user.username}")

        # Migrate Utility Providers
        for provider in UtilityProvider.objects.all():
            user = User.objects.create_user(
                username=f"provider_{provider.utility_id}",
                password="default_password",
                email=provider.email,
                phone_number=provider.phone,
                role='UTILITY_PROVIDER',
                utility_id=provider.utility_id
            )
            print(f"Utility Provider migrated: {user.username}")

        # Migrate Support Admins
        for admin in SupportAdmin.objects.all():
            user = User.objects.create_user(
                username=f"admin_{admin.admin_id}",
                password="default_password",
                email=admin.email,
                phone_number=admin.phone,
                role='SUPPORT_ADMIN',
                admin_id=admin.admin_id
            )
            print(f"Support Admin migrated: {user.username}")

        # Migrate Staff
        for staff in Staff.objects.all():
            user = User.objects.create_user(
                username=f"staff_{staff.staff_id}",
                password="default_password",
                email=staff.email,
                phone_number=staff.phone,
                role='STAFF',
                staff_id=staff.staff_id
            )
            print(f"Staff migrated: {user.username}")

        print("Data migration completed successfully.")
