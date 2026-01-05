from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .models import Event, Photo
from .serializers import EventSerializer, PhotoSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PhotoUploadForm
from django.db.models import Q
from django.core.paginator import Paginator
import zipfile
import os
from django.conf import settings




def event_photos_slide(request, token):
    event = get_object_or_404(Event, token=token)
    photos = event.photos.filter(visible=True)
    return render(request, "events/slide.html", {"event": event, "photos": photos})



def event_manager_select(request):
    events = Event.objects.order_by("-date")
    return render(request, "manager/select_event.html", {"events": events})

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.conf import settings
import os
import zipfile

from .models import Event, Photo
from .forms import PhotoUploadForm


def event_manager(request, token):
    event = get_object_or_404(Event, token=token)

    # -------- GUARDAR CAMBIOS visible / pre_loaded --------
    if request.method == "POST" and request.POST.get("action") == "save":
        photo_ids = request.POST.getlist("photo_id")
        visible_ids = set(request.POST.getlist("visible"))        # IDs de fotos marcadas
        preloaded_ids = set(request.POST.getlist("pre_loaded"))   # IDs de fotos preloaded

        photos = Photo.objects.filter(id__in=photo_ids, event=event)

        for photo in photos:
            pid = str(photo.id)
            photo.visible = pid in visible_ids
            photo.pre_loaded = pid in preloaded_ids

        Photo.objects.bulk_update(photos, ["visible", "pre_loaded"])
        return redirect("event_manager", token=event.token)

    # -------- DESCARGAR FOTOS VISIBLES --------
    if request.method == "POST" and request.POST.get("action") == "download_visible":
        visibles = Photo.objects.filter(event=event, visible=True)
        zip_path = os.path.join(settings.MEDIA_ROOT, f"event_{event.id}_visible.zip")

        with zipfile.ZipFile(zip_path, "w") as zf:
            for photo in visibles:
                if not photo.image:
                    continue
                abs_path = photo.image.path
                arcname = os.path.basename(abs_path)
                zf.write(abs_path, arcname)

        with open(zip_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/zip")
            response["Content-Disposition"] = (
                f'attachment; filename="event_{event.id}_visible.zip"'
            )

        os.remove(zip_path)
        return response

    # -------- SUBIR NUEVAS FOTOS --------
    if request.method == "POST" and request.POST.get("action") == "upload":
        upload_form = PhotoUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            photo = upload_form.save(commit=False)
            photo.event = event
            # visible y pre_loaded se manejan luego desde la grilla
            photo.save()
        return redirect("event_manager", token=event.token)

    # -------- GET: LISTAR FOTOS CON PAGINACIÓN --------
    photo_list = event.photos.all().order_by("-uploaded_at", "-id")
    paginator = Paginator(photo_list, 18)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    upload_form = PhotoUploadForm()


    return render(
        request,
        "manager/event_manager.html",
        {
            "event": event,
            "page_obj": page_obj,
            "upload_form": upload_form,
        },
    )



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
def event_photos_json(request, token):
    event = get_object_or_404(Event, token=token)
    photos = event.photos.filter(
        Q(visible=True) | Q(pre_loaded=True)
    ).order_by("id")
    data = PhotoSerializer(photos, many=True).data
    return Response(data)


def event_photo_upload(request, token):
    event = get_object_or_404(Event, token=token)

    if request.method == "POST":
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.event = event
            photo.save()


            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "ok"})

            return redirect("event_photos_slide", token=token)
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {"status": "error", "errors": form.errors}, status=400
                )
    else:
        form = PhotoUploadForm()

    return render(request, "events/upload.html", {"event": event, "form": form})