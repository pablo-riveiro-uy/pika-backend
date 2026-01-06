from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.views.static import serve
from .views import EventViewSet, PhotoViewSet, event_photos_slide, event_photo_upload, event_photos_json, event_manager, event_manager_select
from django.views.generic import TemplateView 

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'photos', PhotoViewSet, basename='photo')

urlpatterns = [
    path("", TemplateView.as_view(template_name="landing/landing.html"), name="landing"),
    path('', include(router.urls)),
    path("event/<uuid:token>/slide/", event_photos_slide, name="event_photos_slide"),
    path("event/<uuid:token>/upload/", event_photo_upload, name="event_photo_upload"),
    path("event/<uuid:token>/photos-json/", event_photos_json, name="event_photos_json"),
    path("manager/", event_manager_select, name="event_manager_select"),
    path("manager/<uuid:token>/", event_manager, name="event_manager"),
]
# Static
urlpatterns += [
    path(
        "static/<path:path>",
        serve,
        {"document_root": settings.STATIC_ROOT},
        name="static",
    ),
]

# Media
urlpatterns += [
    path(
        "media/<path:path>",
        serve,
        {"document_root": settings.MEDIA_ROOT},
        name="media",
    ),
]