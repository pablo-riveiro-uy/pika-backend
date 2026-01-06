from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
     path(
        "",
        TemplateView.as_view(template_name="landing/landing.html"),
        name="landing",
    ),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),

    # JWT endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

# Static files (admin CSS/JS, etc.)
urlpatterns += [
    path(
        "static/<path:path>",
        serve,
        {"document_root": settings.STATIC_ROOT},
        name="static",
    ),
]

# Media files (qrcodes, fotos, fondos)
urlpatterns += [
    path(
        "media/<path:path>",
        serve,
        {"document_root": settings.MEDIA_ROOT},
        name="media",
    ),
]
