from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, PhotoViewSet, event_photos_json
from . import views

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'photos', PhotoViewSet, basename='photo')


urlpatterns = [
    path('', include(router.urls)),
    path("event/<int:event_id>/slide/", views.event_photos_slide, name="event_photos_slide"),
    path("event/<int:event_id>/upload/", views.event_photo_upload, name="event_photo_upload"),
    path("event/<int:event_id>/photos-json/", event_photos_json, name="event_photos_json"),
]