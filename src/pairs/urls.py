from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatternTypeViewSet, DetectedPatternViewSet

router = DefaultRouter()
router.register(r'pattern-types', PatternTypeViewSet)
router.register(r'patterns', DetectedPatternViewSet, basename='pattern')

urlpatterns = [
    path('', include(router.urls)),
] 