from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Customer, UtilityProvider, SupportAdmin, Staff

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Check the role of the user and create the corresponding profile
        if instance.role == 'CUSTOMER':
            Customer.objects.create(user=instance)
        elif instance.role == 'UTILITY_PROVIDER':
            UtilityProvider.objects.create(user=instance)
        elif instance.role == 'SUPPORT_ADMIN':
            SupportAdmin.objects.create(user=instance)
        elif instance.role == 'STAFF':
            Staff.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Ensure that the profile is saved after user is saved."""
    if instance.role == 'CUSTOMER':
        instance.customer_profile.save()
    elif instance.role == 'UTILITY_PROVIDER':
        instance.utilityprovider_profile.save()
    elif instance.role == 'SUPPORT_ADMIN':
        instance.supportadmin_profile.save()
    elif instance.role == 'STAFF':
        instance.staff_profile.save()

@receiver(post_save, sender=User)
def create_staff_profile(sender, instance, created, **kwargs):
    if created and instance.is_staff:  # Ensure only staff users get a profile
        Staff.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_staff_profile(sender, instance, **kwargs):
    if hasattr(instance, 'staff_profile'):
        instance.staff_profile.save()