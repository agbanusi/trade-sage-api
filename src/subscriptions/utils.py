import logging
from django.utils import timezone
from .models import Subscription
from .config import get_subscription_limits

logger = logging.getLogger(__name__)


def has_active_subscription(user):
    """
    Check if a user has an active subscription
    
    Args:
        user: User instance
        
    Returns:
        bool: True if user has an active subscription, False otherwise
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        subscription = Subscription.objects.get(user=user)
        return subscription.is_active
    except Subscription.DoesNotExist:
        return False
    except Exception as e:
        logger.error(f"Error checking active subscription: {str(e)}")
        return False


def get_user_subscription(user):
    """
    Get a user's subscription
    
    Args:
        user: User instance
        
    Returns:
        Subscription: User's subscription or None
    """
    if not user or not user.is_authenticated:
        return None
    
    try:
        return Subscription.objects.get(user=user)
    except Subscription.DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"Error getting user subscription: {str(e)}")
        return None


def get_user_limits(user):
    """
    Get the feature limits for a user based on their subscription
    
    Args:
        user: User instance
        
    Returns:
        dict: Dictionary of feature limits
    """
    subscription = get_user_subscription(user)
    return get_subscription_limits(subscription)


def can_use_feature(user, feature_name):
    """
    Check if a user can use a specific feature based on their subscription
    
    Args:
        user: User instance
        feature_name: Name of the feature to check
        
    Returns:
        bool: True if user can use the feature, False otherwise
    """
    limits = get_user_limits(user)
    
    # Check if the feature exists in the limits
    if feature_name not in limits:
        # Default to False for unknown features
        logger.warning(f"Unknown feature requested: {feature_name}")
        return False
    
    # Return the feature value (True/False for boolean features)
    return limits[feature_name]


def check_rate_limit(user, limit_name, current_count):
    """
    Check if a user is within their rate limits
    
    Args:
        user: User instance
        limit_name: Name of the limit to check
        current_count: Current count to check against the limit
        
    Returns:
        bool: True if within limits, False if exceeded
    """
    limits = get_user_limits(user)
    
    if limit_name not in limits:
        # Default to a low limit for unknown limits
        logger.warning(f"Unknown rate limit requested: {limit_name}")
        return current_count <= 10
    
    # Return True if within limits, False if exceeded
    return current_count <= limits[limit_name]


def is_premium_timeframe(user, timeframe):
    """
    Check if a timeframe is available for the user's subscription level
    
    Args:
        user: User instance
        timeframe: Timeframe to check
        
    Returns:
        bool: True if the timeframe is available, False otherwise
    """
    limits = get_user_limits(user)
    
    # Check if the timeframe is in the allowed timeframes
    return timeframe in limits.get('timeframes', []) 