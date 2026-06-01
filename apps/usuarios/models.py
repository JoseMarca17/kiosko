from django.db import models
from django.contrib.auth.models import AbstractUser

class Rol(models.Model):
    nombre      = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    activo      = models.BooleanField(default=True)

    class Meta:
        db_table = 'roles'
        verbose_name_plural = 'roles'

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    codigo_estudiante = models.CharField(max_length=20, unique=True, null=True, blank=True)
    telefono          = models.CharField(max_length=20, blank=True)
    rol               = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True, blank=True)
    verificado        = models.BooleanField(default=False)
    ultimo_acceso     = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def es_admin(self):
        return self.rol and self.rol.nombre == 'admin'

    @property
    def es_staff_kiosko(self):
        return self.rol and self.rol.nombre == 'staff_kiosko'

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']