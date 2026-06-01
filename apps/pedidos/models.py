from django.db import models
from django.conf import settings

class EstadoPedido(models.Model):
    nombre      = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    color_hex   = models.CharField(max_length=7, default='#CCCCCC')

    class Meta:
        db_table = 'estados_pedido'

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    codigo_pedido          = models.CharField(max_length=25, unique=True, blank=True)
    usuario                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    estado                 = models.ForeignKey(EstadoPedido, on_delete=models.PROTECT)
    subtotal               = models.DecimalField(max_digits=10, decimal_places=2)
    descuento              = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total                  = models.DecimalField(max_digits=10, decimal_places=2)
    notas_especiales       = models.TextField(blank=True)
    fecha_pedido           = models.DateTimeField(auto_now_add=True)
    fecha_estimada_retiro  = models.DateTimeField(null=True, blank=True)
    cancelado              = models.BooleanField(default=False)
    fecha_cancelacion      = models.DateTimeField(null=True, blank=True)
    motivo_cancelacion     = models.TextField(blank=True)

    class Meta:
        db_table = 'pedidos'
        ordering = ['-fecha_pedido']

    def __str__(self):
        return self.codigo_pedido

    def save(self, *args, **kwargs):
        if not self.codigo_pedido:
            from django.utils import timezone
            from django.db.models import Count
            hoy = timezone.now().date()
            count = Pedido.objects.filter(fecha_pedido__date=hoy).count() + 1
            self.codigo_pedido = f"PED-{hoy.strftime('%Y%m%d')}-{str(count).zfill(4)}"
        super().save(*args, **kwargs)


class DetallePedido(models.Model):
    pedido             = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto           = models.ForeignKey('catalogo.Producto', on_delete=models.PROTECT)
    cantidad           = models.IntegerField()
    precio_unitario    = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal           = models.DecimalField(max_digits=10, decimal_places=2)
    notas              = models.TextField(blank=True)

    class Meta:
        db_table = 'detalle_pedido'

    def __str__(self):
        return f"{self.pedido.codigo_pedido} — {self.producto.nombre}"