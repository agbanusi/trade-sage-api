from django.contrib import admin
from django.urls import include, path, reverse_lazy
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.authentication import JWTAuthentication

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include(("users.urls", "users"))),
    path("api/v1/signals/", include(("signals.urls", "signals"))),
    path("api/v1/pairs/", include(("pairs.urls", "pairs"))),
    path("api/v1/subscriptions/", include(("subscriptions.urls", "subscriptions"))),
    path("api/v1/chart-analysis/", include(("chart_analysis.urls", "chart_analysis"))),
    path(
        "docs/schema.yml",
        SpectacularAPIView.as_view(
            permission_classes=[IsAuthenticated, IsAdminUser],
            authentication_classes=[SessionAuthentication],
        ),
        name="schema",
    ),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            permission_classes=[IsAuthenticated, IsAdminUser],
            authentication_classes=[SessionAuthentication],
        ),
        name="swagger-ui",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url=reverse_lazy("schema"),
            permission_classes=[AllowAny],
            authentication_classes=[JWTAuthentication, SessionAuthentication],
        ),
        name="swagger-ui",
    ),
]
