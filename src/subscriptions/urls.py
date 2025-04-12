from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscriptionPlanViewSet,
    SubscriptionViewSet,
    SubscriptionInvoiceViewSet,
    StripeWebhookView
)

router = DefaultRouter()
router.register(r'plans', SubscriptionPlanViewSet)
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'invoices', SubscriptionInvoiceViewSet, basename='invoice')
router.register(r'stripe', StripeWebhookView, basename='stripe')

urlpatterns = [
    path('', include(router.urls)),
    # Add a direct webhook endpoint that doesn't use the viewset routing
    path('webhook/', StripeWebhookView.as_view({'post': 'webhook'}), name='stripe-webhook'),
] 