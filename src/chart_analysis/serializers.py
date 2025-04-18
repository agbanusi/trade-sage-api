from rest_framework import serializers
from .models import (
    Pair, 
    ChartAnalysis, 
    SavedIndicator, 
    SupportResistanceLevel,
    TechnicalIndicator,
    Timeframe,
    SignalPerformance,
    IndicatorPerformance,
    TimeframePerformance,
    PairPerformance,
    RiskAnalysis,
    UserIndicatorSettings
)


class PairSerializer(serializers.ModelSerializer):
    """
    Serializer for trading pairs
    """
    class Meta:
        model = Pair
        fields = ['id', 'name', 'display_name', 'is_active']


class ChartAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer for chart analysis
    """
    pair_name = serializers.CharField(source='pair.name', read_only=True)
    pair_display_name = serializers.CharField(source='pair.display_name', read_only=True)
    timeframe_display = serializers.CharField(source='get_timeframe_display', read_only=True)
    overall_signal_display = serializers.CharField(source='get_overall_signal_display', read_only=True)
    volatility_level_display = serializers.CharField(source='get_volatility_level_display', read_only=True)
    
    class Meta:
        model = ChartAnalysis
        fields = [
            'id', 'pair', 'pair_name', 'pair_display_name', 'timeframe', 'timeframe_display',
            'current_price', 'change_24h', 'high_24h', 'low_24h',
            'analysis_data', 'overall_signal', 'overall_signal_display',
            'volatility_level', 'volatility_level_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SavedIndicatorSerializer(serializers.ModelSerializer):
    """
    Serializer for saved indicators
    """
    pair_name = serializers.CharField(source='pair.name', read_only=True)
    indicator_type_display = serializers.CharField(source='get_indicator_type_display', read_only=True)
    
    class Meta:
        model = SavedIndicator
        fields = [
            'id', 'pair', 'pair_name', 'user', 'timeframe',
            'indicator_type', 'indicator_type_display', 'parameters',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserIndicatorSettingsSerializer(serializers.ModelSerializer):
    indicator_name = serializers.CharField(source='get_indicator_type_display', read_only=True)
    
    class Meta:
        model = UserIndicatorSettings
        fields = [
            'id', 'user', 'indicator_type', 'indicator_name', 
            'weight', 'is_active', 'indicator_parameters', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SupportResistanceLevelSerializer(serializers.ModelSerializer):
    """
    Serializer for support and resistance levels
    """
    pair_name = serializers.CharField(source='pair.name', read_only=True)
    timeframe_display = serializers.CharField(source='get_timeframe_display', read_only=True)
    level_type_display = serializers.CharField(source='get_level_type_display', read_only=True)
    
    class Meta:
        model = SupportResistanceLevel
        fields = [
            'id', 'pair', 'pair_name', 'user', 'timeframe', 'timeframe_display',
            'level_type', 'level_type_display', 'price_level', 'strength',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class IndicatorChoiceSerializer(serializers.Serializer):
    """
    Serializer for indicator choices
    """
    value = serializers.CharField()
    display_name = serializers.CharField()
    
    
class TimeframeChoiceSerializer(serializers.Serializer):
    """
    Serializer for timeframe choices
    """
    value = serializers.CharField()
    display_name = serializers.CharField()


# Advanced Analytics Serializers

class SignalPerformanceSerializer(serializers.ModelSerializer):
    """
    Serializer for signal performance tracking
    """
    pair_details = PairSerializer(source='pair', read_only=True)
    timeframe_display = serializers.CharField(source='get_timeframe_display', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    signal_type_display = serializers.CharField(source='get_signal_type_display', read_only=True)
    
    class Meta:
        model = SignalPerformance
        fields = [
            'id', 'user', 'pair', 'pair_details', 'timeframe', 'timeframe_display',
            'signal_type', 'signal_type_display', 'entry_price', 'exit_price',
            'target_price', 'stop_loss', 'entry_time', 'exit_time',
            'result', 'result_display', 'profit_loss', 'created', 'updated'
        ]
        read_only_fields = ['created', 'updated']


class IndicatorPerformanceSerializer(serializers.ModelSerializer):
    """
    Serializer for indicator performance
    """
    pair_details = PairSerializer(source='pair', read_only=True)
    indicator_type_display = serializers.CharField(source='get_indicator_type_display', read_only=True)
    timeframe_display = serializers.CharField(source='get_timeframe_display', read_only=True)
    
    class Meta:
        model = IndicatorPerformance
        fields = [
            'id', 'user', 'indicator_type', 'indicator_type_display',
            'timeframe', 'timeframe_display', 'pair', 'pair_details',
            'accuracy', 'sample_size', 'last_updated', 'created', 'updated'
        ]
        read_only_fields = ['created', 'updated', 'last_updated']


class TimeframePerformanceSerializer(serializers.ModelSerializer):
    """
    Serializer for timeframe performance
    """
    timeframe_display = serializers.CharField(source='get_timeframe_display', read_only=True)
    
    class Meta:
        model = TimeframePerformance
        fields = [
            'id', 'user', 'timeframe', 'timeframe_display', 'accuracy',
            'sample_size', 'win_count', 'loss_count', 'last_updated', 
            'created', 'updated'
        ]
        read_only_fields = ['created', 'updated', 'last_updated']


class PairPerformanceSerializer(serializers.ModelSerializer):
    """
    Serializer for pair performance
    """
    pair_details = PairSerializer(source='pair', read_only=True)
    
    class Meta:
        model = PairPerformance
        fields = [
            'id', 'user', 'pair', 'pair_details', 'accuracy',
            'sample_size', 'win_count', 'loss_count', 'last_updated',
            'created', 'updated'
        ]
        read_only_fields = ['created', 'updated', 'last_updated']


class RiskAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer for risk analysis
    """
    class Meta:
        model = RiskAnalysis
        fields = [
            'id', 'user', 'win_rate', 'avg_risk_reward', 'max_drawdown',
            'profit_factor', 'total_trades', 'winning_trades', 'losing_trades',
            'avg_win_size', 'avg_loss_size', 'last_updated', 'created', 'updated'
        ]
        read_only_fields = ['created', 'updated', 'last_updated'] 