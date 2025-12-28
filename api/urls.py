from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, PhotoViewSet, event_photos_slide, event_photo_upload, event_photos_json

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'photos', PhotoViewSet, basename='photo')

urlpatterns = [
    path('', include(router.urls)),
    path("event/<uuid:token>/slide/", event_photos_slide, name="event_photos_slide"),
    path("event/<uuid:token>/upload/", event_photo_upload, name="event_photo_upload"),
    path("event/<uuid:token>/photos-json/", event_photos_json, name="event_photos_json"),
]
