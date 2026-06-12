from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class Rol(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_rol')
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'roles'
        verbose_name_plural = 'roles'

    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre_completo, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        
        # Obtener o crear el rol de estudiante (default)
        try:
            rol_estudiante = Rol.objects.get(nombre='estudiante')
        except Rol.DoesNotExist:
            rol_estudiante = Rol.objects.create(nombre='estudiante', descripcion='Usuario estándar')
            
        extra_fields.setdefault('rol', rol_estudiante)
        user = self.model(email=email, nombre_completo=nombre_completo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre_completo, password=None, **extra_fields):
        # Obtener o crear el rol de admin
        try:
            rol_admin = Rol.objects.get(nombre='admin')
        except Rol.DoesNotExist:
            rol_admin = Rol.objects.create(nombre='admin', descripcion='Administrador con acceso total')

        extra_fields['rol'] = rol_admin
        extra_fields.setdefault('verificado', True)
        user = self.create_user(email=email, nombre_completo=nombre_completo, password=password, **extra_fields)
        return user


class Usuario(AbstractBaseUser):
    id = models.AutoField(primary_key=True, db_column='id_usuario')
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255, db_column='password_hash')
    nombre_completo = models.CharField(max_length=255)
    codigo_estudiante = models.CharField(max_length=20, unique=True, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, db_column='id_rol', default=2)
    verificado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True, db_column='activo')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True, db_column='ultimo_acceso')

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre_completo']

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.nombre_completo or self.email

    @property
    def es_admin(self):
        return self.rol and self.rol.nombre == 'admin'

    @property
    def es_staff_kiosko(self):
        return self.rol and self.rol.nombre == 'staff_kiosko'

    @property
    def is_active(self):
        return self.activo

    @property
    def is_staff(self):
        return self.es_admin or self.es_staff_kiosko

    @property
    def is_superuser(self):
        return self.es_admin

    @property
    def username(self):
        return self.email

    def get_full_name(self):
        return self.nombre_completo

    def get_short_name(self):
        return self.nombre_completo

    def has_perm(self, perm, obj=None):
        return self.es_admin

    def has_module_perms(self, app_label):
        return self.es_admin