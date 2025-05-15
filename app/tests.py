from django.test import TestCase
from django.utils.timezone import now
from app.models import (
    User, Customer, UtilityProvider, SupportAdmin, Staff, 
    Item, Meter, Bill, Payment, Issue, Feedback
)


class ModelsTestCase(TestCase):

    def setUp(self):
        self.user_customer = User.objects.create_user(username="test_customer", password="password", role="CUSTOMER")
        self.user_provider = User.objects.create_user(username="test_provider", password="password", role="UTILITY_PROVIDER")
        
        # Creating profile instances
        self.customer = Customer.objects.create(user=self.user_customer)
        self.provider = UtilityProvider.objects.create(user=self.user_provider)
        
        # Other models setup
        self.item = Item.objects.create(item_id="ITEM001", item_name="Electricity Tariff")
        self.meter = Meter.objects.create(
            meter_id="M00001", meter_reading=100, tariff_rate=0.15, customer=self.customer
        )
        self.bill = Bill.objects.create(
            bill_id="B00001", customer=self.customer, amount=100.00, due_date=now().date(),
            paid=False, creation_date=now().date(), penalty_fee=5.00
        )
        self.payment = Payment.objects.create(
            payment_id="P00001", customer=self.customer, payment_date=now().date(),
            payment_method="FPX", amount=105.00
        )
        self.issue = Issue.objects.create(
            issue_id="I00001", customer=self.customer, title="Power Outage",
            description="Power outage for 2 hours", status="open", ticket_id="T00001"
        )
        self.feedback = Feedback.objects.create(
            feedback_id="F00001", customer=self.customer, rating=5, comment="Great service",
            feedback_date=now().date()
        )

    def test_customer_profile_creation(self):
        """Test that Customer profile is created successfully."""
        self.assertEqual(self.customer.identifier[0], 'C')
        self.assertTrue(self.customer.identifier.startswith("C"))

    def test_utility_provider_profile_creation(self):
        """Test that UtilityProvider profile is created successfully."""
        self.assertEqual(self.provider.identifier[0], 'U')
        self.assertTrue(self.provider.identifier.startswith("U"))

    def test_meter_association(self):
        """Test the association between Customer and Meter."""
        self.assertEqual(self.meter.customer, self.customer)

    def test_bill_creation(self):
        """Test Bill creation and fields."""
        self.assertEqual(self.bill.amount, 100.00)
        self.assertEqual(self.bill.customer, self.customer)

    def test_payment_creation(self):
        """Test Payment creation."""
        self.assertEqual(self.payment.amount, 105.00)
        self.assertEqual(self.payment.payment_method, "FPX")

    def test_issue_creation(self):
        """Test Issue creation."""
        self.assertEqual(self.issue.status, "open")
        self.assertEqual(self.issue.customer, self.customer)

    def test_feedback_creation(self):
        """Test Feedback creation."""
        self.assertEqual(self.feedback.rating, 5)
        self.assertEqual(self.feedback.comment, "Great service")
