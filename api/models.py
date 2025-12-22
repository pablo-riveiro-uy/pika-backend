from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models




class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    qrcode = models.ImageField(upload_to="qrcodes/", blank=True, null=True)

    def get_absolute_url(self):
        return reverse("event_photos_slide", kwargs={"event_id": self.id})

    def generate_qrcode(self):
        # URL que apunta al slide de fotos de este evento
        url = self.get_absolute_url()

        # Generar el QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Guardar la imagen en memoria
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Guardar en el campo ImageField
        filename = f"event_{self.id}_qrcode.png"
        self.qrcode.save(filename, ContentFile(buffer.read()), save=False)
        buffer.close()

    def __str__(self):
        return f"{self.title} ({self.date})"


class Photo(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="photos/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    visible = models.BooleanField(default=False, blank=True)
    pre_loaded = models.BooleanField(default=False, blank=True)
    def __str__(self):
        return f"Photo for {self.event.title}"