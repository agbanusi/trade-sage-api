from django.shortcuts import render
import stripe
import logging
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SubscriptionPlan, Subscription, SubscriptionInvoice
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer, SubscriptionInvoiceSerializer
from .permissions import IsSubscriptionOwner

logger = logging.getLogger(__name__)

# Initialize Stripe API - this will be imported from settings
stripe.api_key = settings.STRIPE_API_KEY
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing subscription plans
    """
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user subscriptions
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSubscriptionOwner]
    
    def get_queryset(self):
        """
        Return subscriptions for the current user only
        """
        return Subscription.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new subscription
        """
        # Check if the user already has a subscription
        if Subscription.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "User already has a subscription"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the plan
        plan_id = request.data.get('plan')
        if not plan_id:
            return Response(
                {"detail": "Plan is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            plan = SubscriptionPlan.objects.get(pk=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {"detail": "Invalid plan selected"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a Stripe customer or retrieve existing one
        customer = self._get_or_create_stripe_customer(request.user)
        
        # Create the subscription data
        subscription_data = {
            'user': request.user.id,
            'plan': plan.id,
            'stripe_customer_id': customer.id,
            'status': 'incomplete',
        }
        
        serializer = self.get_serializer(data=subscription_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Use Stripe to create a checkout session
        checkout_session = self._create_checkout_session(
            customer_id=customer.id,
            price_id=plan.stripe_price_id,
            subscription_id=serializer.instance.id
        )
        
        # Return the checkout session URL
        return Response({
            'subscription': serializer.data,
            'checkout_url': checkout_session.url
        }, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """
        Cancel a subscription
        """
        subscription = self.get_object()
        
        if subscription.stripe_subscription_id:
            try:
                # Cancel the subscription in Stripe
                stripe_subscription = stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                
                # Update local subscription
                subscription.cancel_at_period_end = True
                subscription.save()
                
                serializer = self.get_serializer(subscription)
                return Response(serializer.data)
            except stripe.error.StripeError as e:
                logger.error(f"Stripe error when canceling subscription: {str(e)}")
                return Response(
                    {"detail": "Error canceling subscription"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # If there's no Stripe subscription ID, just delete it
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get the current user's subscription
        """
        try:
            subscription = Subscription.objects.get(user=request.user)
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response(
                {"detail": "User has no active subscription"}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """
        Reactivate a canceled subscription
        """
        subscription = self.get_object()
        
        # Check if the subscription is canceled but still active
        if not subscription.cancel_at_period_end:
            return Response(
                {"detail": "Subscription is not canceled"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Update the subscription in Stripe
            stripe_subscription = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=False
            )
            
            # Update local subscription
            subscription.cancel_at_period_end = False
            subscription.save()
            
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error when reactivating subscription: {str(e)}")
            return Response(
                {"detail": "Error reactivating subscription"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def change_plan(self, request, pk=None):
        """
        Change subscription plan
        """
        subscription = self.get_object()
        new_plan_id = request.data.get('plan')
        
        if not new_plan_id:
            return Response(
                {"detail": "New plan is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_plan = SubscriptionPlan.objects.get(pk=new_plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {"detail": "Invalid plan selected"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Update the subscription in Stripe
            stripe_subscription = stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                items=[{
                    'id': stripe.Subscription.retrieve(subscription.stripe_subscription_id)['items']['data'][0]['id'],
                    'price': new_plan.stripe_price_id,
                }],
                proration_behavior='create_prorations'
            )
            
            # Update local subscription
            subscription.plan = new_plan
            subscription.save()
            
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error when changing plan: {str(e)}")
            return Response(
                {"detail": "Error changing subscription plan"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _get_or_create_stripe_customer(self, user):
        """
        Get or create a Stripe customer for the user
        """
        # Check if user already has a subscription with customer id
        try:
            subscription = Subscription.objects.get(user=user)
            if subscription.stripe_customer_id:
                # Return existing customer
                return stripe.Customer.retrieve(subscription.stripe_customer_id)
        except Subscription.DoesNotExist:
            pass
        
        # Create a new customer
        customer = stripe.Customer.create(
            email=user.email,
            name=user.name,
            metadata={'user_id': user.id}
        )
        
        return customer
    
    def _create_checkout_session(self, customer_id, price_id, subscription_id):
        """
        Create a Stripe checkout session for subscription payment
        """
        success_url = f"{settings.FRONTEND_URL}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{settings.FRONTEND_URL}/subscription/cancel"
        
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'subscription_id': subscription_id
            }
        )
        
        return checkout_session


class SubscriptionInvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing subscription invoices
    """
    serializer_class = SubscriptionInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return invoices for the current user's subscription only
        """
        return SubscriptionInvoice.objects.filter(subscription__user=self.request.user)


class StripeWebhookView(viewsets.ViewSet):
    """
    ViewSet for handling Stripe webhooks
    """
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def webhook(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            # Invalid payload
            logger.error(f"Invalid Stripe webhook payload: {str(e)}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            logger.error(f"Invalid Stripe webhook signature: {str(e)}")
            return HttpResponse(status=400)
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            self._handle_checkout_completed(event)
        elif event['type'] == 'invoice.paid':
            self._handle_invoice_paid(event)
        elif event['type'] == 'invoice.payment_failed':
            self._handle_invoice_payment_failed(event)
        elif event['type'] == 'customer.subscription.updated':
            self._handle_subscription_updated(event)
        elif event['type'] == 'customer.subscription.deleted':
            self._handle_subscription_deleted(event)
        
        return HttpResponse(status=200)
    
    def _handle_checkout_completed(self, event):
        """
        Handle checkout.session.completed event
        """
        session = event['data']['object']
        
        # Get the subscription ID from metadata
        subscription_id = session.get('metadata', {}).get('subscription_id')
        if not subscription_id:
            logger.error("No subscription_id in checkout session metadata")
            return
        
        try:
            subscription = Subscription.objects.get(id=subscription_id)
            
            # Update subscription with Stripe subscription ID
            stripe_subscription_id = session.get('subscription')
            if stripe_subscription_id:
                stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)
                
                subscription.stripe_subscription_id = stripe_subscription_id
                subscription.status = 'active'
                subscription.current_period_start = timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_start, tz=timezone.get_current_timezone()
                )
                subscription.current_period_end = timezone.datetime.fromtimestamp(
                    stripe_subscription.current_period_end, tz=timezone.get_current_timezone()
                )
                subscription.save()
                
                logger.info(f"Subscription {subscription_id} activated successfully")
        except Subscription.DoesNotExist:
            logger.error(f"Subscription {subscription_id} not found")
        except Exception as e:
            logger.error(f"Error handling checkout.session.completed: {str(e)}")
    
    def _handle_invoice_paid(self, event):
        """
        Handle invoice.paid event
        """
        invoice = event['data']['object']
        stripe_subscription_id = invoice.get('subscription')
        
        if not stripe_subscription_id:
            return
        
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=stripe_subscription_id)
            
            # Create an invoice record
            SubscriptionInvoice.objects.create(
                subscription=subscription,
                stripe_invoice_id=invoice.get('id'),
                amount_paid=invoice.get('amount_paid') / 100,  # Convert from cents
                billing_period_start=timezone.datetime.fromtimestamp(
                    invoice.get('period_start'), tz=timezone.get_current_timezone()
                ),
                billing_period_end=timezone.datetime.fromtimestamp(
                    invoice.get('period_end'), tz=timezone.get_current_timezone()
                ),
                status='paid'
            )
            
            # Update subscription period
            stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)
            subscription.status = 'active'
            subscription.current_period_start = timezone.datetime.fromtimestamp(
                stripe_subscription.current_period_start, tz=timezone.get_current_timezone()
            )
            subscription.current_period_end = timezone.datetime.fromtimestamp(
                stripe_subscription.current_period_end, tz=timezone.get_current_timezone()
            )
            subscription.save()
            
            logger.info(f"Invoice {invoice.get('id')} paid for subscription {subscription.id}")
        except Subscription.DoesNotExist:
            logger.error(f"Subscription with Stripe ID {stripe_subscription_id} not found")
        except Exception as e:
            logger.error(f"Error handling invoice.paid: {str(e)}")
    
    def _handle_invoice_payment_failed(self, event):
        """
        Handle invoice.payment_failed event
        """
        invoice = event['data']['object']
        stripe_subscription_id = invoice.get('subscription')
        
        if not stripe_subscription_id:
            return
        
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=stripe_subscription_id)
            
            # Update subscription status
            subscription.status = 'past_due'
            subscription.save()
            
            logger.info(f"Invoice payment failed for subscription {subscription.id}")
        except Subscription.DoesNotExist:
            logger.error(f"Subscription with Stripe ID {stripe_subscription_id} not found")
        except Exception as e:
            logger.error(f"Error handling invoice.payment_failed: {str(e)}")
    
    def _handle_subscription_updated(self, event):
        """
        Handle customer.subscription.updated event
        """
        stripe_subscription = event['data']['object']
        stripe_subscription_id = stripe_subscription.get('id')
        
        if not stripe_subscription_id:
            return
        
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=stripe_subscription_id)
            
            # Update subscription status and period
            subscription.status = stripe_subscription.get('status')
            subscription.cancel_at_period_end = stripe_subscription.get('cancel_at_period_end', False)
            subscription.current_period_start = timezone.datetime.fromtimestamp(
                stripe_subscription.get('current_period_start'), tz=timezone.get_current_timezone()
            )
            subscription.current_period_end = timezone.datetime.fromtimestamp(
                stripe_subscription.get('current_period_end'), tz=timezone.get_current_timezone()
            )
            subscription.save()
            
            logger.info(f"Subscription {subscription.id} updated")
        except Subscription.DoesNotExist:
            logger.error(f"Subscription with Stripe ID {stripe_subscription_id} not found")
        except Exception as e:
            logger.error(f"Error handling customer.subscription.updated: {str(e)}")
    
    def _handle_subscription_deleted(self, event):
        """
        Handle customer.subscription.deleted event
        """
        stripe_subscription = event['data']['object']
        stripe_subscription_id = stripe_subscription.get('id')
        
        if not stripe_subscription_id:
            return
        
        try:
            subscription = Subscription.objects.get(stripe_subscription_id=stripe_subscription_id)
            
            # Update subscription status
            subscription.status = 'expired'
            subscription.save()
            
            logger.info(f"Subscription {subscription.id} expired")
        except Subscription.DoesNotExist:
            logger.error(f"Subscription with Stripe ID {stripe_subscription_id} not found")
        except Exception as e:
            logger.error(f"Error handling customer.subscription.deleted: {str(e)}")
