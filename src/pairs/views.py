from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import PatternType, DetectedPattern, PatternCategory, PatternStatus
from .serializers import (
    PatternTypeSerializer, 
    DetectedPatternSerializer,
    PatternSummarySerializer
)


class PatternTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to view pattern types.
    Read-only since pattern types are managed by the system.
    """
    queryset = PatternType.objects.filter(is_active=True)
    serializer_class = PatternTypeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'category']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category if specified
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category.upper())
            
        # Filter by bullish/bearish if specified
        direction = self.request.query_params.get('direction')
        if direction:
            if direction.lower() == 'bullish':
                queryset = queryset.filter(is_bullish=True)
            elif direction.lower() == 'bearish':
                queryset = queryset.filter(is_bullish=False)
                
        return queryset
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Return a list of all pattern categories
        """
        categories = [
            {'value': cat[0], 'display': cat[1]}
            for cat in PatternCategory.choices
        ]
        return Response(categories)


class DetectedPatternViewSet(viewsets.ModelViewSet):
    """
    API endpoint for detected patterns.
    """
    serializer_class = DetectedPatternSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['pattern_type__name', 'pair__name', 'description']
    ordering_fields = ['detection_time', 'confidence', 'completion_percentage']
    
    def get_queryset(self):
        """Filter patterns based on query parameters"""
        # Start with all patterns, or only the user's if they're not staff
        if self.request.user.is_staff:
            queryset = DetectedPattern.objects.all()
        else:
            queryset = DetectedPattern.objects.filter(
                Q(user=self.request.user) | Q(user__isnull=True)
            )
            
        # Apply filters based on query params
        
        # Filter by pair
        pair = self.request.query_params.get('pair')
        if pair:
            queryset = queryset.filter(pair__name=pair)
            
        # Filter by timeframe
        timeframe = self.request.query_params.get('timeframe')
        if timeframe:
            queryset = queryset.filter(timeframe=timeframe)
            
        # Filter by pattern category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(pattern_type__category=category.upper())
            
        # Filter by pattern name
        pattern = self.request.query_params.get('pattern')
        if pattern:
            queryset = queryset.filter(pattern_type__name__icontains=pattern)
            
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status.upper())
            
        # Filter by direction (bullish/bearish)
        direction = self.request.query_params.get('direction')
        if direction:
            if direction.lower() == 'bullish':
                queryset = queryset.filter(pattern_type__is_bullish=True)
            elif direction.lower() == 'bearish':
                queryset = queryset.filter(pattern_type__is_bullish=False)
                
        # Filter by minimum confidence
        min_confidence = self.request.query_params.get('min_confidence')
        if min_confidence and min_confidence.isdigit():
            queryset = queryset.filter(confidence__gte=min_confidence)
            
        # Filter by time range
        time_range = self.request.query_params.get('time_range')
        if time_range:
            now = timezone.now()
            if time_range == '24h':
                start_time = now - timedelta(hours=24)
            elif time_range == '7d':
                start_time = now - timedelta(days=7)
            elif time_range == '30d':
                start_time = now - timedelta(days=30)
            else:
                # Default to 24 hours if invalid range
                start_time = now - timedelta(hours=24)
                
            queryset = queryset.filter(detection_time__gte=start_time)
        
        return queryset
    
    def get_serializer_class(self):
        """Use the summary serializer for list endpoints"""
        if self.action == 'list':
            return PatternSummarySerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        """Automatically assign the current user when creating a pattern"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update the status of a pattern (e.g., to mark as complete or failed)
        """
        pattern = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {"error": "Status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            new_status = new_status.upper()
            if new_status not in [s[0] for s in PatternStatus.choices]:
                raise ValueError(f"Invalid status: {new_status}")
                
            # Update status and completion time if moving to a final state
            if new_status in [PatternStatus.COMPLETE, PatternStatus.FAILED, PatternStatus.TARGET_HIT]:
                pattern.status = new_status
                if not pattern.completion_time:
                    pattern.completion_time = timezone.now()
            else:
                pattern.status = new_status
                
            # Update completion percentage if provided
            completion_percentage = request.data.get('completion_percentage')
            if completion_percentage is not None:
                try:
                    pattern.completion_percentage = float(completion_percentage)
                except ValueError:
                    pass
                    
            pattern.save()
            return Response(DetectedPatternSerializer(pattern).data)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def active_patterns(self, request):
        """
        Get currently active patterns (forming or complete but not failed)
        """
        queryset = self.get_queryset().filter(
            status__in=[PatternStatus.FORMING, PatternStatus.COMPLETE]
        ).order_by('-confidence')
        
        # Limit to recent patterns (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        queryset = queryset.filter(detection_time__gte=week_ago)
        
        # Use limit if provided, otherwise default to 10
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
            
        queryset = queryset[:limit]
        serializer = PatternSummarySerializer(queryset, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def recently_completed(self, request):
        """
        Get patterns that recently completed (target hit or failed)
        """
        queryset = self.get_queryset().filter(
            status__in=[PatternStatus.TARGET_HIT, PatternStatus.FAILED]
        ).order_by('-completion_time')
        
        # Limit to patterns from the last 30 days
        month_ago = timezone.now() - timedelta(days=30)
        queryset = queryset.filter(completion_time__gte=month_ago)
        
        # Use limit if provided, otherwise default to 10
        limit = request.query_params.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
            
        queryset = queryset[:limit]
        serializer = PatternSummarySerializer(queryset, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get patterns grouped by category
        """
        result = {}
        for category in PatternCategory.choices:
            category_code = category[0]
            category_name = category[1]
            
            queryset = self.get_queryset().filter(
                pattern_type__category=category_code
            ).order_by('-detection_time')[:5]
            
            serializer = PatternSummarySerializer(queryset, many=True)
            result[category_code] = {
                'name': category_name,
                'patterns': serializer.data
            }
            
        return Response(result) 