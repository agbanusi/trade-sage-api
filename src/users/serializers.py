from rest_framework import serializers
from .models import NotificationSettings

class NotificationSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for user notification settings
    """
    class Meta:
        model = NotificationSettings
        fields = [
            'id', 'user', 'signal_notifications', 
            'email_notifications', 'push_notifications', 'sound_alerts',
            'signal_alerts', 'price_alerts', 'pattern_recognition', 'economic_news_alerts',
            'max_signals_per_day', 'signal_quality_filter',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] 