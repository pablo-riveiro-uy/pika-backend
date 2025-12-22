from rest_framework import serializers
from .models import Event, Photo

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['id', 'event', 'image', 'uploaded_at', 'visible', 'pre_loaded']


class EventSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'created_at', 'photos', 'qrcode']
  

    def create(self, validated_data):
        event = Event.objects.create(**validated_data)
        event.generate_qrcode()
        event.save(update_fields=["qrcode"])
        return event
