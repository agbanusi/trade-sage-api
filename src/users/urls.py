from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import NotificationSettingsViewSet

router = DefaultRouter()
router.register(r'notification-settings', NotificationSettingsViewSet, basename='notification-settings')

urlpatterns = [
    path("", include("djoser.urls")),
    path("", include("djoser.urls.jwt")),
    path("", include(router.urls)),
]
