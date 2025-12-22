from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Event, Photo
from .serializers import EventSerializer, PhotoSerializer

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

@login_required
def event_photos_slide(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    photos = event.photos.filter(visible=True)
    return render(request, "events/slide.html", {"event": event, "photos": photos})



class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Cada usuario solo ve sus propios eventos
        return Event.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Asigna automáticamente el usuario autenticado al crear un evento
        serializer.save(user=self.request.user)


class PhotoViewSet(viewsets.ModelViewSet):
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Cada usuario solo ve las fotos de sus eventos
        return Photo.objects.filter(event__user=self.request.user)

    def perform_create(self, serializer):
        # Al crear una foto, se asegura que esté vinculada a un evento del usuario
        event = serializer.validated_data.get('event')
        if event.user != self.request.user:
            raise PermissionError("No puedes subir fotos a eventos de otros usuarios.")
        serializer.save()