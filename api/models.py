from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from qrcode.image.pil import PilImage
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import models


class Event(models.Model):
    THEME_CHOICES = [
        ("light", "Claro"),
        ("dark", "Oscuro"),
    ]

    FONT_CHOICES = [
        ("system", "Sistema"),
        ("montserrat", "Montserrat"),
        ("roboto", "Roboto"),
        ("lora", "Lora (serif)"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    qrcode = models.ImageField(upload_to="qrcodes/", blank=True, null=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    theme = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default="dark",
    )
    font = models.CharField(
        max_length=20,
        choices=FONT_CHOICES,
        default="system",
    )
    slider_background = models.ImageField(
        upload_to="slider_backgrounds/",
        blank=True,
        null=True,
    )
    is_square_screen = models.BooleanField(
        default=False,
        help_text="Marca esta opción si la pantalla del evento es cuadrada.",
    )

    def get_upload_url(self):
        relative = reverse("event_photo_upload", kwargs={"token": self.token})
        return settings.SITE_BASE_URL.rstrip("/") + relative

    def generate_qrcode(self):
        url = self.get_upload_url()

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white", image_factory=PilImage)

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        filename = f"event_{self.id}_qrcode.png"
        self.qrcode.save(filename, ContentFile(buffer.read()), save=False)
        buffer.close()

    def save(self, *args, **kwargs):
        # Si es un evento nuevo (no tiene id todavía), generamos el token
        if not self.pk:
            self.token = uuid.uuid4()

        # Guardamos primero para que tenga id
        super().save(*args, **kwargs)

        # Solo generamos el QR si no existe todavía
        if not self.qrcode:
            self.generate_qrcode()
            # Guardamos de nuevo para que se guarde el QR en el campo qrcode
            super().save(update_fields=["qrcode"])

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