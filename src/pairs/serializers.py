from rest_framework import serializers
from .models import PatternType, DetectedPattern
from signals.serializers import TradingPairSerializer


class PatternTypeSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = PatternType
        fields = [
            'id', 'name', 'category', 'category_display', 'description', 
            'is_bullish', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DetectedPatternSerializer(serializers.ModelSerializer):
    pattern_type_details = PatternTypeSerializer(source='pattern_type', read_only=True)
    pair_details = TradingPairSerializer(source='pair', read_only=True)
    timeframe_display = serializers.CharField(source='get_timeframe_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    time_since_detection = serializers.CharField(read_only=True)
    risk_reward_ratio = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    pattern_name = serializers.CharField(source='pattern_type.name', read_only=True)
    pattern_category = serializers.CharField(source='pattern_type.category', read_only=True)
    
    class Meta:
        model = DetectedPattern
        fields = [
            'id', 'pair', 'pair_details', 'pattern_type', 'pattern_type_details',
            'pattern_name', 'pattern_category', 'user', 'timeframe', 'timeframe_display',
            'status', 'status_display', 'confidence', 'price_at_detection',
            'entry_zone_low', 'entry_zone_high', 'stop_loss', 'target_price',
            'secondary_target', 'pattern_start_time', 'detection_time', 
            'completion_time', 'description', 'completion_percentage',
            'chart_image', 'ratios', 'metadata', 'time_since_detection',
            'risk_reward_ratio'
        ]
        read_only_fields = ['detection_time', 'time_since_detection', 'risk_reward_ratio']


class PatternSummarySerializer(serializers.ModelSerializer):
    """A simpler serializer for listing patterns with less detail"""
    pattern_name = serializers.CharField(source='pattern_type.name', read_only=True)
    pair_name = serializers.CharField(source='pair.name', read_only=True)
    is_bullish = serializers.BooleanField(read_only=True)
    time_since_detection = serializers.CharField(read_only=True)
    
    class Meta:
        model = DetectedPattern
        fields = [
            'id', 'pattern_name', 'pair_name', 'timeframe', 'status',
            'confidence', 'completion_percentage', 'is_bullish',
            'time_since_detection'
        ] 