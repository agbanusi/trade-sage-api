from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, SubscriptionInvoice


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """
    Serializer for the SubscriptionPlan model
    """
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'description', 'price', 'billing_period', 
            'features', 'is_active', 'created', 'updated'
        ]
        read_only_fields = ['created', 'updated']


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Subscription model
    """
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'plan', 'plan_details', 'status', 
            'current_period_start', 'current_period_end', 'cancel_at_period_end',
            'is_active', 'created', 'updated'
        ]
        read_only_fields = ['created', 'updated', 'current_period_start', 'current_period_end']


class SubscriptionInvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for the SubscriptionInvoice model
    """
    class Meta:
        model = SubscriptionInvoice
        fields = [
            'id', 'subscription', 'stripe_invoice_id', 'amount_paid',
            'billing_period_start', 'billing_period_end', 'status',
            'created', 'updated'
        ]
        read_only_fields = ['created', 'updated'] 