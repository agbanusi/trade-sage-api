import logging
import re
from django.http import JsonResponse
from django.conf import settings
from .models import Subscription

logger = logging.getLogger(__name__)


class PremiumAccessMiddleware:
    """
    Middleware to check if a user has premium access before allowing them to access premium features.
    This middleware should be applied specifically to views that require premium access.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile the list of premium endpoint patterns
        self.premium_patterns = getattr(settings, 'PREMIUM_ENDPOINTS', [])
        self.compiled_patterns = [re.compile(pattern) for pattern in self.premium_patterns]
    
    def __call__(self, request):
        # Check if the current path matches any premium endpoint patterns
        path = request.path_info
        
        # Skip the middleware for certain requests
        if not self._is_premium_endpoint(path):
            return self.get_response(request)
        
        # Allow unauthenticated requests to be handled by the view
        # (which will then return 401 Unauthorized)
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Check if the user has a valid premium subscription
        has_premium_access = self._check_premium_access(request.user)
        
        if has_premium_access:
            # User has premium access, proceed with the request
            return self.get_response(request)
        else:
            # User doesn't have premium access, return 403 Forbidden
            return JsonResponse(
                {"detail": "This endpoint requires a premium subscription"}, 
                status=403
            )
    
    def _is_premium_endpoint(self, path):
        """
        Check if the path matches any premium endpoint patterns
        """
        for pattern in self.compiled_patterns:
            if pattern.match(path):
                return True
        return False
    
    def _check_premium_access(self, user):
        """
        Check if the user has an active premium subscription
        """
        try:
            subscription = Subscription.objects.get(user=user)
            return subscription.is_active
        except Subscription.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error checking premium access: {str(e)}")
            # In case of an error, default to denying access
            return False 