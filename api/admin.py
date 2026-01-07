from django.contrib import admin
from .models import Event, Photo


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ('image', 'visible', 'pre_loaded', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'user', 'created_at', 'id', 'token', 'theme', 'font', 'is_square_screen')
    list_filter = ('date', 'created_at', 'theme', 'font')
    fields = (
        'user', 'title', 'description', 'date',
        'theme', 'font', 'slider_background',
        'qrcode', 'token', 'created_at',
        'is_square_screen'
    )
    readonly_fields = ('qrcode', 'token', 'created_at')
    inlines = [PhotoInline]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('event', 'uploaded_at', 'visible', 'pre_loaded', 'id')
    list_filter = ('uploaded_at', 'event', 'visible', 'pre_loaded')
