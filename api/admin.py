from django.contrib import admin
from .models import Event, Photo


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ('image', 'visible', 'pre_loaded', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'user', 'created_at', 'id', 'token')
    search_fields = ('title', 'description', 'token')
    list_filter = ('date', 'created_at')
    inlines = [PhotoInline]

    # Opcional: hacer que el token se vea más corto en la lista
    def token(self, obj):
        return str(obj.token)
    token.short_description = 'Token (UUID)'
    token.admin_order_field = 'token'


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('event', 'uploaded_at', 'visible', 'pre_loaded', 'id')
    list_filter = ('uploaded_at', 'event', 'visible', 'pre_loaded')
