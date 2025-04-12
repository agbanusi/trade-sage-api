from rest_framework import permissions


class IsSubscriptionOwner(permissions.BasePermission):
    """
    Permission to only allow owners of a subscription to access it
    """
    
    def has_object_permission(self, request, view, obj):
        # Object must have a user attribute that matches the request user
        return obj.user == request.user 