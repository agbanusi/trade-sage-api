from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import NotificationSettings
from .serializers import NotificationSettingsSerializer


class NotificationSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notification settings
    """
    serializer_class = NotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return notification settings for the current user only"""
        return NotificationSettings.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating settings"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_settings(self, request):
        """
        Get the notification settings for the current user.
        If settings don't exist, create default settings.
        """
        try:
            settings = NotificationSettings.objects.get(user=request.user)
        except NotificationSettings.DoesNotExist:
            # Create default settings for new user
            settings = NotificationSettings.objects.create(user=request.user)
        
        serializer = self.get_serializer(settings)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_settings(self, request):
        """
        Update notification settings for the current user
        """
        try:
            settings = NotificationSettings.objects.get(user=request.user)
        except NotificationSettings.DoesNotExist:
            # Create settings if they don't exist
            settings = NotificationSettings.objects.create(user=request.user)
        
        serializer = self.get_serializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 