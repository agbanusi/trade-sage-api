from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TradingPairViewSet, SignalViewSet,
    InstrumentViewSet, WeightedInstrumentViewSet,
    SignalReportViewSet
)

router = DefaultRouter()
router.register(r'trading-pairs', TradingPairViewSet)
router.register(r'signals', SignalViewSet, basename='signal')
router.register(r'instruments', InstrumentViewSet)
router.register(r'weighted-instruments', WeightedInstrumentViewSet, basename='weighted-instrument')
router.register(r'reports', SignalReportViewSet, basename='signal-report')

urlpatterns = [
    path('', include(router.urls)),
] 