from django.contrib import admin
from .models import SubscriptionPlan, Subscription, SubscriptionInvoice


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'billing_period', 'price', 'is_active', 'created', 'updated')
    list_filter = ('billing_period', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('name', 'billing_period')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_plan_name', 'status', 'current_period_end', 'cancel_at_period_end', 'created')
    list_filter = ('status', 'cancel_at_period_end')
    search_fields = ('user__email', 'stripe_customer_id', 'stripe_subscription_id')
    ordering = ('-created',)
    date_hierarchy = 'created'
    
    def get_plan_name(self, obj):
        return obj.plan.name if obj.plan else "No Plan"
    get_plan_name.short_description = 'Plan'


@admin.register(SubscriptionInvoice)
class SubscriptionInvoiceAdmin(admin.ModelAdmin):
    list_display = ('get_user_email', 'stripe_invoice_id', 'amount_paid', 'status', 'billing_period_start', 'created')
    list_filter = ('status',)
    search_fields = ('subscription__user__email', 'stripe_invoice_id')
    ordering = ('-created',)
    date_hierarchy = 'created'
    
    def get_user_email(self, obj):
        return obj.subscription.user.email
    get_user_email.short_description = 'User'
