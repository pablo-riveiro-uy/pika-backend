from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = "Crea el grupo GlobalAdmin con todos los permisos"

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="GlobalAdmin")

        # Asignar todos los permisos de todos los modelos
        for content_type in ContentType.objects.all():
            for codename in ["add", "change", "delete", "view"]:
                try:
                    perm = Permission.objects.get(
                        content_type=content_type,
                        codename=f"{codename}_{content_type.model}"
                    )
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    pass

        self.stdout.write(
            self.style.SUCCESS("Grupo GlobalAdmin creado y con todos los permisos")
        )
