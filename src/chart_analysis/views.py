from django.shortcuts import render
import logging
import random
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from subscriptions.middleware import PremiumAccessMiddleware
from subscriptions.utils import (
    has_active_subscription,
    get_user_limits,
    is_premium_timeframe
)

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
    RiskAnalysis
)
from .serializers import (
    PairSerializer,
    ChartAnalysisSerializer,
    SavedIndicatorSerializer,
    SupportResistanceLevelSerializer,
    IndicatorChoiceSerializer,
    TimeframeChoiceSerializer,
    SignalPerformanceSerializer,
    IndicatorPerformanceSerializer,
    TimeframePerformanceSerializer,
    PairPerformanceSerializer,
    RiskAnalysisSerializer
)

logger = logging.getLogger(__name__)


class PairViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing trading pairs
    """
    queryset = Pair.objects.filter(is_active=True)
    serializer_class = PairSerializer
    permission_classes = [permissions.IsAuthenticated]


class ChartAnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet for chart analysis - premium users only
    """
    serializer_class = ChartAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return chart analyses for the current user only
        """
        return ChartAnalysis.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new chart analysis, checking premium status for timeframes
        """
        # Check if user has access to requested timeframe
        timeframe = request.data.get('timeframe', Timeframe.ONE_HOUR)
        if not is_premium_timeframe(request.user, timeframe):
            return Response(
                {"detail": f"Timeframe '{timeframe}' requires a premium subscription"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Add user to request data
        data = request.data.copy()
        data['user'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def analyze(self, request):
        """
        Get a real-time analysis for a specific pair and timeframe
        """
        pair_id = request.query_params.get('pair')
        timeframe = request.query_params.get('timeframe', Timeframe.ONE_HOUR)
        
        if not pair_id:
            return Response(
                {"detail": "Pair ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user has access to requested timeframe
        if not is_premium_timeframe(request.user, timeframe):
            return Response(
                {"detail": f"Timeframe '{timeframe}' requires a premium subscription"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            pair = Pair.objects.get(id=pair_id)
        except Pair.DoesNotExist:
            return Response(
                {"detail": "Invalid pair selected"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate mock analysis data
        # In a real implementation, this would call a service to perform the analysis
        analysis = self._generate_mock_analysis(pair, timeframe, request.user)
        serializer = self.get_serializer(analysis)
        
        return Response(serializer.data)
    
    def _generate_mock_analysis(self, pair, timeframe, user):
        """
        Generate mock chart analysis data for demonstration purposes
        In a real implementation, this would use actual market data and analysis
        """
        # Check if analysis already exists for this pair/timeframe
        try:
            analysis = ChartAnalysis.objects.get(
                pair=pair,
                timeframe=timeframe,
                user=user
            )
        except ChartAnalysis.DoesNotExist:
            # Create a new analysis object
            analysis = ChartAnalysis(
                pair=pair,
                timeframe=timeframe,
                user=user
            )
        
        # Generate random price data (for demo purposes)
        if pair.name == 'EUR/USD':
            base_price = 1.08
        elif pair.name == 'BTC/USD':
            base_price = 60000
        else:
            base_price = random.uniform(1, 100)
        
        # Set price data
        analysis.current_price = base_price + random.uniform(-0.05, 0.05)
        analysis.change_24h = random.uniform(-2.0, 2.0)
        analysis.high_24h = analysis.current_price * (1 + random.uniform(0.01, 0.05))
        analysis.low_24h = analysis.current_price * (1 - random.uniform(0.01, 0.05))
        
        # Set technical analysis data
        oscillators_buy = random.randint(0, 7)
        oscillators_neutral = random.randint(0, 7 - oscillators_buy)
        oscillators_sell = 7 - oscillators_buy - oscillators_neutral
        
        moving_avgs_buy = random.randint(0, 5)
        moving_avgs_neutral = random.randint(0, 5 - moving_avgs_buy)
        moving_avgs_sell = 5 - moving_avgs_buy - moving_avgs_neutral
        
        patterns_count = random.randint(2, 5)
        
        analysis.analysis_data = {
            'oscillators': {
                'buy': oscillators_buy,
                'neutral': oscillators_neutral,
                'sell': oscillators_sell
            },
            'moving_averages': {
                'buy': moving_avgs_buy,
                'neutral': moving_avgs_neutral,
                'sell': moving_avgs_sell
            },
            'patterns': {
                'count': patterns_count,
                'neutral': random.randint(0, patterns_count)
            }
        }
        
        # Determine overall signal
        total_buy = oscillators_buy + moving_avgs_buy
        total_sell = oscillators_sell + moving_avgs_sell
        
        if total_buy > total_sell + 3:
            analysis.overall_signal = 'buy'
        elif total_sell > total_buy + 3:
            analysis.overall_signal = 'sell'
        else:
            analysis.overall_signal = 'neutral'
        
        # Set volatility
        volatility_options = ['low', 'moderate', 'high']
        analysis.volatility_level = random.choice(volatility_options)
        
        analysis.save()
        return analysis


class SavedIndicatorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing saved indicators
    """
    serializer_class = SavedIndicatorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return saved indicators for the current user only
        """
        return SavedIndicator.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new saved indicator
        """
        # Check if user has premium access for advanced indicators
        if not has_active_subscription(request.user):
            premium_indicators = [
                TechnicalIndicator.ICHIMOKU,
                TechnicalIndicator.FIBONACCI
            ]
            if request.data.get('indicator_type') in premium_indicators:
                return Response(
                    {"detail": "This indicator requires a premium subscription"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Add user to request data
        data = request.data.copy()
        data['user'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def available_indicators(self, request):
        """
        Get a list of available indicators based on subscription level
        """
        indicators = []
        for indicator in TechnicalIndicator.choices:
            indicators.append({
                'value': indicator[0],
                'display_name': indicator[1]
            })
        
        serializer = IndicatorChoiceSerializer(indicators, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available_timeframes(self, request):
        """
        Get a list of available timeframes based on subscription level
        """
        user_limits = get_user_limits(request.user)
        available_timeframes = user_limits.get('timeframes', [])
        
        timeframes = []
        for tf in Timeframe.choices:
            if tf[0] in available_timeframes:
                timeframes.append({
                    'value': tf[0],
                    'display_name': tf[1]
                })
        
        serializer = TimeframeChoiceSerializer(timeframes, many=True)
        return Response(serializer.data)


class SupportResistanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing support and resistance levels
    """
    serializer_class = SupportResistanceLevelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return support/resistance levels created by the current user
        or shared publicly
        """
        return SupportResistanceLevel.objects.filter(
            Q(created_by=self.request.user)
        )
    
    def create(self, request, *args, **kwargs):
        """
        Create a new support/resistance level
        """
        # Check if user has premium access for advanced timeframes
        timeframe = request.data.get('timeframe', Timeframe.ONE_HOUR)
        if not is_premium_timeframe(request.user, timeframe):
            return Response(
                {"detail": f"Timeframe '{timeframe}' requires a premium subscription"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Add user to request data
        data = request.data.copy()
        data['created_by'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def for_pair(self, request):
        """
        Get support/resistance levels for a specific pair
        """
        pair_id = request.query_params.get('pair')
        timeframe = request.query_params.get('timeframe', Timeframe.ONE_HOUR)
        
        if not pair_id:
            return Response(
                {"detail": "Pair ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if timeframe is available for user
        if not is_premium_timeframe(request.user, timeframe):
            return Response(
                {"detail": f"Timeframe '{timeframe}' requires a premium subscription"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        levels = SupportResistanceLevel.objects.filter(
            pair_id=pair_id,
            timeframe=timeframe
        ).filter(
            Q(created_by=self.request.user)
        ).order_by('price_level')
        
        serializer = self.get_serializer(levels, many=True)
        return Response(serializer.data)


# Advanced Analytics ViewSets

class SignalPerformanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for signal performance tracking
    """
    serializer_class = SignalPerformanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return signal performances for the current user only
        """
        return SignalPerformance.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new signal performance record
        """
        # Check if user has premium access
        if not has_active_subscription(request.user):
            return Response(
                {"detail": "Signal performance tracking requires a premium subscription"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Add user to request data
        data = request.data.copy()
        data['user'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AdvancedAnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for advanced analytics dashboard
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def indicator_performance(self, request):
        """
        Get performance data for various indicators
        """
        # Check if user has premium access
        if not has_active_subscription(request.user):
            return Response(
                {"detail": "Advanced analytics requires a premium subscription"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get or generate indicator performance data
        indicators = self._get_indicator_performance(request.user)
        
        return Response(indicators)
    
    @action(detail=False, methods=['get'])
    def timeframe_performance(self, request):
        """
        Get performance data by timeframe
        """
        # Check if user has premium access
        if not has_active_subscription(request.user):
            return Response(
                {"detail": "Advanced analytics requires a premium subscription"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get or generate timeframe performance data
        timeframes = self._get_timeframe_performance(request.user)
        
        return Response(timeframes)
    
    @action(detail=False, methods=['get'])
    def pair_performance(self, request):
        """
        Get performance data by currency pair
        """
        # Check if user has premium access
        if not has_active_subscription(request.user):
            return Response(
                {"detail": "Advanced analytics requires a premium subscription"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get or generate pair performance data
        pairs = self._get_pair_performance(request.user)
        
        return Response(pairs)
    
    @action(detail=False, methods=['get'])
    def risk_analysis(self, request):
        """
        Get risk analysis metrics
        """
        # Check if user has premium access
        if not has_active_subscription(request.user):
            return Response(
                {"detail": "Advanced analytics requires a premium subscription"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get or generate risk analysis data
        risk_data = self._get_risk_analysis(request.user)
        
        return Response(risk_data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Get all advanced analytics data for the dashboard
        """
        # Check if user has premium access
        if not has_active_subscription(request.user):
            return Response(
                {"detail": "Advanced analytics requires a premium subscription"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Combine all analytics for the dashboard
        dashboard_data = {
            'indicator_performance': self._get_indicator_performance(request.user),
            'timeframe_performance': self._get_timeframe_performance(request.user),
            'pair_performance': self._get_pair_performance(request.user),
            'risk_analysis': self._get_risk_analysis(request.user)
        }
        
        return Response(dashboard_data)
    
    def _get_indicator_performance(self, user):
        """
        Get or generate indicator performance data
        """
        # Check if data exists and return it, otherwise generate mock data
        indicators = IndicatorPerformance.objects.filter(user=user)
        
        if not indicators.exists():
            # Generate mock data for demonstration
            indicator_data = []
            for indicator in TechnicalIndicator.choices:
                accuracy = round(random.uniform(60, 95), 2)
                indicator_data.append({
                    'indicator': indicator[0],
                    'name': indicator[1],
                    'accuracy': accuracy,
                    'sample_size': random.randint(50, 300)
                })
            return indicator_data
        
        # If real data exists, format and return it
        serializer = IndicatorPerformanceSerializer(indicators, many=True)
        return serializer.data
    
    def _get_timeframe_performance(self, user):
        """
        Get or generate timeframe performance data
        """
        # Check if data exists and return it, otherwise generate mock data
        timeframes = TimeframePerformance.objects.filter(user=user)
        
        if not timeframes.exists():
            # Generate mock data for demonstration
            timeframe_data = {
                'average': 65,
                'timeframes': []
            }
            
            for tf in Timeframe.choices:
                # Generate a random accuracy between 55% and 85%
                accuracy = round(random.uniform(55, 85), 2)
                timeframe_data['timeframes'].append({
                    'timeframe': tf[0],
                    'name': tf[1],
                    'accuracy': accuracy,
                    'sample_size': random.randint(30, 200)
                })
            
            return timeframe_data
        
        # If real data exists, format and return it
        serializer = TimeframePerformanceSerializer(timeframes, many=True)
        avg_accuracy = sum(tf.accuracy for tf in timeframes) / timeframes.count()
        
        return {
            'average': round(avg_accuracy, 2),
            'timeframes': serializer.data
        }
    
    def _get_pair_performance(self, user):
        """
        Get or generate pair performance data
        """
        # Check if data exists and return it, otherwise generate mock data
        pair_performances = PairPerformance.objects.filter(user=user)
        
        if not pair_performances.exists():
            # Generate mock data for demonstration
            pair_data = []
            
            # Get all active pairs
            pairs = Pair.objects.filter(is_active=True)
            
            for pair in pairs:
                # Generate a random accuracy between 65% and 85%
                accuracy = round(random.uniform(65, 85), 2)
                pair_data.append({
                    'pair': pair.name,
                    'accuracy': accuracy,
                    'sample_size': random.randint(30, 150)
                })
            
            return pair_data
        
        # If real data exists, format and return it
        serializer = PairPerformanceSerializer(pair_performances, many=True)
        return serializer.data
    
    def _get_risk_analysis(self, user):
        """
        Get or generate risk analysis data
        """
        # Check if data exists and return it, otherwise generate mock data
        try:
            risk_analysis = RiskAnalysis.objects.get(user=user)
            serializer = RiskAnalysisSerializer(risk_analysis)
            return serializer.data
        except RiskAnalysis.DoesNotExist:
            # Generate mock data for demonstration
            win_rate = round(random.uniform(65, 85), 2)
            avg_rr = round(random.uniform(1.5, 3.0), 2)
            max_drawdown = round(random.uniform(5, 15), 2)
            profit_factor = round(random.uniform(1.5, 2.5), 2)
            
            return {
                'win_rate': win_rate,
                'avg_risk_reward': f"1:{avg_rr}",
                'max_drawdown': f"{max_drawdown}%",
                'profit_factor': profit_factor,
                'total_trades': random.randint(100, 500),
                'winning_trades': random.randint(70, 300),
                'losing_trades': random.randint(30, 200)
            }
