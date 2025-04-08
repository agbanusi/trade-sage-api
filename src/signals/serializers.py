from rest_framework import serializers
from .models import TradingPair, Signal, Instrument, WeightedInstrument, SignalReport


class TradingPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradingPair
        fields = ['id', 'name', 'base_asset', 'quote_asset', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class WeightedInstrumentSerializer(serializers.ModelSerializer):
    pair_name = serializers.CharField(source='pair.name', read_only=True)
    instrument_name = serializers.CharField(source='instrument.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = WeightedInstrument
        fields = [
            'id', 'user', 'user_email', 'pair', 'pair_name', 'instrument', 
            'instrument_name', 'weight', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
    def validate(self, data):
        """
        Check that:
        1. The total weights per user and pair don't exceed 100
        2. The user doesn't have more than 5 instruments per pair
        """
        user = data.get('user')
        pair = data.get('pair')
        weight = data.get('weight')
        
        # If we're updating an existing instance
        instance = self.instance
        
        # Check 5-instrument limit
        if user and pair and not instance:
            # Only check on creation, not update
            existing_count = WeightedInstrument.objects.filter(
                user=user, 
                pair=pair
            ).count()
            
            if existing_count >= 5:
                raise serializers.ValidationError(
                    "Maximum of 5 instruments allowed per user and trading pair"
                )
        
        # Calculate total weights excluding this instance (if updating)
        total_weight = 0
        if user and pair:
            queryset = WeightedInstrument.objects.filter(user=user, pair=pair)
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            total_weight = queryset.aggregate(
                total=serializers.Sum('weight')
            )['total'] or 0
            
        # Add this weight
        if weight:
            total_weight += weight
            
        if total_weight > 100:
            raise serializers.ValidationError(
                f"Total weights ({total_weight}) exceed 100 for this user and pair"
            )
            
        return data


class SignalSerializer(serializers.ModelSerializer):
    pair_name = serializers.CharField(source='pair.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Signal
        fields = [
            'id', 'user', 'user_email', 'pair', 'pair_name', 'signal_type', 
            'price', 'entry_price', 'stop_loss', 'take_profit', 
            'potential_gain', 'risk_reward_ratio', 'confidence', 
            'timestamp', 'is_executed', 'execution_time'
        ]
        read_only_fields = ['timestamp', 'user']


class SignalReportSerializer(serializers.ModelSerializer):
    pair_name = serializers.CharField(source='pair.name', read_only=True)
    user_email = serializers.SerializerMethodField()
    
    class Meta:
        model = SignalReport
        fields = [
            'id', 'timestamp', 'user', 'user_email', 'pair', 'pair_name',
            'price', 'buy_signals', 'sell_signals', 'hold_signals',
            'avg_confidence', 'avg_risk_reward', 'data'
        ]
        read_only_fields = ['timestamp', 'user']
        
    def get_user_email(self, obj):
        """Return user email or None for aggregate reports."""
        if obj.user:
            return obj.user.email
        return None 