import django_filters
from .models import ChartAnalysis, SavedIndicator

class ChartAnalysisFilter(django_filters.FilterSet):
    """
    Filter for chart analysis objects
    """
    class Meta:
        model = ChartAnalysis
        fields = ['pair', 'timeframe', 'user']


class SavedIndicatorFilter(django_filters.FilterSet):
    """
    Filter for saved indicator objects
    """
    class Meta:
        model = SavedIndicator
        fields = ['pair', 'indicator_type', 'user'] 