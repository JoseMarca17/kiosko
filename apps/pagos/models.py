from django.db import models
from django.conf import settings

class QRKiosko(models.Model):
    banco          = models.CharField(max_length=100)
    titular        = models.CharField(max_length=255)
    numero_cuenta  = models.CharField(max_length=50, blank=True)
    imagen_qr      = models.ImageField(upload_to='qr_kiosko/')
    activo         = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qr_kiosko'

    def __str__(self):
        return f"{self.banco} — {self.titular}"


class Transaccion(models.Model):
    ESTADO_CHOICES = [
        ('pendiente_validacion', 'Pendiente validación'),
        ('aprobado',             'Aprobado'),
        ('rechazado',            'Rechazado'),
    ]
    pedido            = models.OneToOneField('pedidos.Pedido', on_delete=models.PROTECT, related_name='transaccion')
    qr_usado          = models.ForeignKey(QRKiosko, on_delete=models.PROTECT)
    monto             = models.DecimalField(max_digits=10, decimal_places=2)
    estado            = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='pendiente_validacion')
    fecha_transaccion = models.DateTimeField(auto_now_add=True)
    validado_por      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_validacion  = models.DateTimeField(null=True, blank=True)
    notas_validacion  = models.TextField(blank=True)

    class Meta:
        db_table = 'transacciones'

    def __str__(self):
        return f"{self.pedido.codigo_pedido} — {self.estado}"


class Comprobante(models.Model):
    transaccion      = models.ForeignKey(Transaccion, on_delete=models.CASCADE, related_name='comprobantes')
    imagen           = models.ImageField(upload_to='comprobantes/')
    monto_detectado  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    hash_imagen      = models.CharField(max_length=64, unique=True, blank=True)
    fecha_subida     = models.DateTimeField(auto_now_add=True)
    validado         = models.BooleanField(default=False)

    class Meta:
        db_table = 'comprobantes'

    def save(self, *args, **kwargs):
        if self.imagen and not self.hash_imagen:
            import hashlib
            self.imagen.seek(0)
            self.hash_imagen = hashlib.sha256(self.imagen.read()).hexdigest()
            self.imagen.seek(0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comprobante {self.transaccion.pedido.codigo_pedido}"