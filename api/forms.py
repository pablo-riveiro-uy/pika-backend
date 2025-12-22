from django import forms
from .models import Photo

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ["image"]
        widgets = {
            "image": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*",
                    "capture": "environment",  # o "user" para cámara frontal
                }
            )
        }
