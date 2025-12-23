from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Event, Photo
from .serializers import EventSerializer, PhotoSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PhotoUploadForm
from django.db.models import Q


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

@api_view(["GET"])
@permission_classes([AllowAny])  # o IsAuthenticated si querés protegerlo
def event_photos_json(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    photos = event.photos.filter(
        Q(visible=True) | Q(pre_loaded=True)
    ).order_by("id")
    data = PhotoSerializer(photos, many=True).data
    return Response(data)


def event_photo_upload(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            # Aquí se fija el evento en el backend
            photo.event = event
            photo.save()
            return redirect("event_photos_slide", event_id=event.id)
    else:
        form = PhotoUploadForm()

    return render(request, "events/upload.html", {"event": event, "form": form})