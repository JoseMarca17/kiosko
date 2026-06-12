from django.db import models
from django.conf import settings

class EstadoPedido(models.Model):
    id          = models.AutoField(primary_key=True, db_column='id_estado')
    nombre      = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    color_hex   = models.CharField(max_length=7, default='#CCCCCC')

    class Meta:
        db_table = 'estados_pedido'

    def __str__(self):
        return self.nombre

    @property
    def display_nombre(self):
        return self.nombre.replace('_', ' ').title()


class Pedido(models.Model):
    id                     = models.AutoField(primary_key=True, db_column='id_pedido')
    codigo_pedido          = models.CharField(max_length=25, unique=True, blank=True)
    usuario                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column='id_usuario')
    estado                 = models.ForeignKey(EstadoPedido, on_delete=models.PROTECT, db_column='id_estado', default=1)
    subtotal               = models.DecimalField(max_digits=10, decimal_places=2)
    descuento              = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total                  = models.DecimalField(max_digits=10, decimal_places=2)
    notas_especiales       = models.TextField(null=True, blank=True)
    fecha_pedido           = models.DateTimeField(auto_now_add=True)
    fecha_estimada_retiro  = models.DateTimeField(null=True, blank=True)
    cancelado              = models.BooleanField(default=False)
    fecha_cancelacion      = models.DateTimeField(null=True, blank=True)
    motivo_cancelacion     = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'pedidos'
        ordering = ['-fecha_pedido']

    def __str__(self):
        return self.codigo_pedido

    def save(self, *args, **kwargs):
        if not self.codigo_pedido:
            from django.utils import timezone
            from datetime import datetime, time
            local_now = timezone.localtime(timezone.now())
            local_date = local_now.date()
            start_of_day = timezone.make_aware(datetime.combine(local_date, time.min))
            end_of_day = timezone.make_aware(datetime.combine(local_date, time.max))
            count = Pedido.objects.filter(fecha_pedido__gte=start_of_day, fecha_pedido__lte=end_of_day).count() + 1
            self.codigo_pedido = f"PED-{local_date.strftime('%Y%m%d')}-{str(count).zfill(4)}"
        super().save(*args, **kwargs)


class DetallePedido(models.Model):
    id                 = models.AutoField(primary_key=True, db_column='id_detalle')
    pedido             = models.ForeignKey(Pedido, on_delete=models.CASCADE, db_column='id_pedido', related_name='detalles')
    producto           = models.ForeignKey('catalogo.Producto', on_delete=models.PROTECT, db_column='id_producto')
    oferta             = models.ForeignKey('catalogo.Oferta', on_delete=models.SET_NULL, null=True, blank=True, db_column='id_oferta')
    cantidad           = models.IntegerField()
    precio_unitario    = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subtotal           = models.DecimalField(max_digits=10, decimal_places=2)
    notas              = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'detalle_pedido'

    def __str__(self):
        return f"{self.pedido.codigo_pedido} — {self.producto.nombre}"