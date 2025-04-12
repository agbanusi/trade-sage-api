from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import BaseModel


class SubscriptionPlan(BaseModel):
    """
    Model representing a subscription plan
    """
    name = models.CharField(max_length=100)
    stripe_price_id = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    billing_period = models.CharField(
        max_length=20,
        choices=[
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ],
        default='monthly'
    )
    features = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.name} ({self.get_billing_period_display()})"


class Subscription(BaseModel):
    """
    Model representing a user's subscription
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        related_name='subscriptions'
    )
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('canceled', 'Canceled'),
            ('past_due', 'Past Due'),
            ('unpaid', 'Unpaid'),
            ('incomplete', 'Incomplete'),
            ('trialing', 'Trialing'),
            ('expired', 'Expired'),
        ],
        default='active'
    )
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    
    @property
    def is_active(self):
        """
        Check if subscription is active
        """
        return (
            self.status == 'active' or 
            self.status == 'trialing'
        ) and self.current_period_end > timezone.now()
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name if self.plan else 'No Plan'}"


class SubscriptionInvoice(BaseModel):
    """
    Model for tracking subscription payments
    """
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    stripe_invoice_id = models.CharField(max_length=100)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    billing_period_start = models.DateTimeField()
    billing_period_end = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('paid', 'Paid'),
            ('unpaid', 'Unpaid'),
            ('void', 'Void'),
        ],
        default='unpaid'
    )
    
    def __str__(self):
        return f"Invoice {self.stripe_invoice_id} - {self.subscription.user.email}"
