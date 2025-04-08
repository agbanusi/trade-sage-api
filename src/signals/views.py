from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TradingPair, Signal, Instrument, WeightedInstrument, SignalReport
from .serializers import (
    TradingPairSerializer, SignalSerializer, 
    InstrumentSerializer, WeightedInstrumentSerializer,
    SignalReportSerializer
)
from .services import TradingDecisionService


class TradingPairViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows trading pairs to be viewed or edited.
    """
    queryset = TradingPair.objects.all()
    serializer_class = TradingPairSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def generate_signal(self, request, pk=None):
        """
        Generate a trading signal for this pair.
        """
        pair = self.get_object()
        
        # Get the current price from the request
        price = request.data.get('price')
        if not price:
            return Response(
                {"error": "Price is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get the strategy from the request (optional)
        strategy = request.data.get('strategy', 'default')
        
        # Generate a signal for the current user
        service = TradingDecisionService(pair, request.user)
        signal = service.generate_signal(price, strategy)
        
        # Return the signal
        serializer = SignalSerializer(signal)
        return Response(serializer.data)


class InstrumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows trading instruments to be viewed or edited.
    """
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    permission_classes = [IsAuthenticated]


class WeightedInstrumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows weighted instruments to be viewed or edited.
    """
    serializer_class = WeightedInstrumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only return weighted instruments for the current user."""
        return WeightedInstrument.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Save the user automatically."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_configuration(self, request):
        """
        Get weighted instruments configuration for the current user,
        grouped by trading pair.
        """
        user_instruments = self.get_queryset()
        
        # Group by pair
        result = {}
        pairs = TradingPair.objects.filter(
            weighted_instruments__user=request.user
        ).distinct()
        
        for pair in pairs:
            pair_instruments = user_instruments.filter(pair=pair)
            serializer = self.get_serializer(pair_instruments, many=True)
            result[pair.name] = serializer.data
            
        return Response(result)


class SignalViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows trading signals to be viewed or edited.
    """
    serializer_class = SignalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return signals filtered by user/pair/type as needed."""
        queryset = Signal.objects.all()
        
        # If user is not staff, only show their signals
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        # Filter by trading pair if specified
        pair = self.request.query_params.get('pair')
        if pair:
            queryset = queryset.filter(pair__name=pair)
            
        # Filter by signal type if specified
        signal_type = self.request.query_params.get('signal_type')
        if signal_type:
            queryset = queryset.filter(signal_type=signal_type)
            
        return queryset
    
    def perform_create(self, serializer):
        """Save the user automatically."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """
        Execute a trading signal.
        """
        signal = self.get_object()
        
        # Don't execute already executed signals
        if signal.is_executed:
            return Response(
                {"error": "Signal already executed"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Execute the signal
        service = TradingDecisionService(signal.pair, request.user)
        success = service.execute_signal(signal)
        
        if success:
            return Response({"status": "signal executed"})
        else:
            return Response(
                {"error": "Failed to execute signal"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SignalReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows viewing signal reports.
    Read-only since reports are generated by the system.
    """
    serializer_class = SignalReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return reports filtered by user/pair as needed."""
        queryset = SignalReport.objects.all()
        
        # If user is not staff, only show their reports or aggregate reports
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                user=self.request.user
            )
        
        # Filter by trading pair if specified
        pair = self.request.query_params.get('pair')
        if pair:
            queryset = queryset.filter(pair__name=pair)
            
        # Filter by user if specified and requester is staff
        user = self.request.query_params.get('user')
        if user and self.request.user.is_staff:
            queryset = queryset.filter(user__email=user)
            
        # Filter by aggregate (no user) if specified
        aggregate = self.request.query_params.get('aggregate')
        if aggregate and aggregate.lower() == 'true':
            queryset = queryset.filter(user__isnull=True)
            
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        """
        Get reports for the current user, grouped by trading pair.
        """
        # Get the most recent report for each pair
        result = {}
        
        # Get all pairs the user has reports for
        pairs = TradingPair.objects.filter(
            reports__user=request.user
        ).distinct()
        
        for pair in pairs:
            # Get the most recent report
            try:
                report = SignalReport.objects.filter(
                    user=request.user,
                    pair=pair
                ).latest('timestamp')
                
                serializer = self.get_serializer(report)
                result[pair.name] = serializer.data
            except SignalReport.DoesNotExist:
                pass
            
        return Response(result) 