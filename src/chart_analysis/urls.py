from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PairViewSet,
    ChartAnalysisViewSet,
    SavedIndicatorViewSet,
    SupportResistanceViewSet,
    SignalPerformanceViewSet,
    AdvancedAnalyticsViewSet,
    UserIndicatorSettingsViewSet
)

router = DefaultRouter()
router.register(r'pairs', PairViewSet)
router.register(r'analysis', ChartAnalysisViewSet, basename='chart-analysis')
router.register(r'indicators', SavedIndicatorViewSet, basename='saved-indicator')
router.register(r'support-resistance', SupportResistanceViewSet, basename='support-resistance')
router.register(r'signal-performance', SignalPerformanceViewSet, basename='signal-performance')
router.register(r'advanced-analytics', AdvancedAnalyticsViewSet, basename='advanced-analytics')
router.register(r'indicator-settings', UserIndicatorSettingsViewSet, basename='indicator-settings')

urlpatterns = [
    path('', include(router.urls)),
] 