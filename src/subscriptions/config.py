"""
Configuration file for subscription plans.
This defines the features and limitations for each subscription tier.
"""

# Free tier limits
FREE_TIER_LIMITS = {
    'max_patterns_per_day': 5,
    'max_saved_patterns': 10,
    'timeframes': ['1h', '4h', 'daily'],
    'pattern_types': ['basic'],
    'realtime_alerts': False,
    'export_data': False,
    'api_rate_limit': 100,  # per day
}

# Pro tier limits (monthly)
MONTHLY_PRO_TIER_LIMITS = {
    'max_patterns_per_day': 50,
    'max_saved_patterns': 100,
    'timeframes': ['5m', '15m', '30m', '1h', '4h', 'daily', 'weekly'],
    'pattern_types': ['all'],
    'realtime_alerts': True,
    'export_data': True,
    'api_rate_limit': 1000,  # per day
    'priority_support': True,
}

# Pro tier limits (yearly)
YEARLY_PRO_TIER_LIMITS = {
    'max_patterns_per_day': 100,
    'max_saved_patterns': 500,
    'timeframes': ['1m', '5m', '15m', '30m', '1h', '4h', 'daily', 'weekly', 'monthly'],
    'pattern_types': ['all'],
    'realtime_alerts': True,
    'export_data': True,
    'api_rate_limit': 5000,  # per day
    'priority_support': True,
}

# Premium endpoints that require a subscription
PREMIUM_ENDPOINTS = [
    # Pattern recognition endpoints
    r'^/api/v1/pairs/detect-realtime/$',
    r'^/api/v1/pairs/bulk-analyze/$',
    r'^/api/v1/pairs/export/$',
    
    # Chart analysis endpoints
    r'^/api/v1/chart-analysis/analysis/analyze/$',
    r'^/api/v1/chart-analysis/analysis/[0-9]+/$',
    r'^/api/v1/chart-analysis/indicators/available_timeframes/$',
    r'^/api/v1/chart-analysis/support-resistance/for_pair/$',
    
    # Advanced analytics endpoints
    r'^/api/v1/chart-analysis/advanced-analytics/.*$',
    r'^/api/v1/chart-analysis/signal-performance/.*$',
]

# Mapping of subscription types to their limits
SUBSCRIPTION_LIMITS = {
    'free': FREE_TIER_LIMITS,
    'monthly': MONTHLY_PRO_TIER_LIMITS,
    'yearly': YEARLY_PRO_TIER_LIMITS,
}

# Function to get limits for a specific subscription
def get_subscription_limits(subscription=None):
    """
    Get the feature limits for a specific subscription
    
    Args:
        subscription: Subscription instance or None for free tier
        
    Returns:
        dict: Dictionary of feature limits
    """
    if subscription is None or not subscription.is_active:
        return FREE_TIER_LIMITS
    
    # Get the subscription plan's billing period
    billing_period = subscription.plan.billing_period
    
    if billing_period == 'yearly':
        return YEARLY_PRO_TIER_LIMITS
    elif billing_period == 'monthly':
        return MONTHLY_PRO_TIER_LIMITS
    else:
        # Fallback to free tier
        return FREE_TIER_LIMITS 