from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User,
    Item,
    Customer,
    Meter,
    UtilityProvider,
    SupportAdmin,
    Staff,
    Bill,
    Payment,
    Issue,
    Feedback
)

# Register models in one place
admin.site.register(User, UserAdmin)
admin.site.register(Item)
admin.site.register(Customer)
admin.site.register(Meter)
admin.site.register(UtilityProvider)
admin.site.register(SupportAdmin)
admin.site.register(Staff)
admin.site.register(Bill)
admin.site.register(Payment)
admin.site.register(Issue)
admin.site.register(Feedback)