from django.db import models

class Categoria(models.Model):
    nombre      = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    icono_url   = models.CharField(max_length=255, blank=True)
    orden       = models.IntegerField(default=0)
    activo      = models.BooleanField(default=True)

    class Meta:
        db_table = 'categorias'
        ordering = ['orden']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre      = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    categoria   = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    imagen      = models.ImageField(upload_to='productos/', blank=True, null=True)
    destacado   = models.BooleanField(default=False)
    activo      = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'productos'

    def __str__(self):
        return self.nombre

    def precio_actual(self):
        """Retorna el precio con descuento si hay oferta activa"""
        from django.utils import timezone
        oferta = self.ofertas.filter(
            activo=True,
            fecha_inicio__lte=timezone.now(),
            fecha_fin__gte=timezone.now()
        ).first()
        if not oferta:
            return self.precio_base
        if oferta.tipo_descuento == 'porcentaje':
            return self.precio_base * (1 - oferta.valor_descuento / 100)
        return max(self.precio_base - oferta.valor_descuento, 0)


class Inventario(models.Model):
    producto            = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='inventario')
    stock_actual        = models.IntegerField(default=0)
    stock_minimo        = models.IntegerField(default=5)
    stock_maximo        = models.IntegerField(default=100)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventario'

    def __str__(self):
        return f"{self.producto.nombre} — stock: {self.stock_actual}"

    @property
    def stock_bajo(self):
        return self.stock_actual <= self.stock_minimo


class Oferta(models.Model):
    TIPO_CHOICES = [
        ('porcentaje', 'Porcentaje'),
        ('monto_fijo', 'Monto fijo'),
    ]
    producto        = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='ofertas')
    tipo_descuento  = models.CharField(max_length=20, choices=TIPO_CHOICES)
    valor_descuento = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion     = models.CharField(max_length=255, blank=True)
    fecha_inicio    = models.DateTimeField()
    fecha_fin       = models.DateTimeField()
    activo          = models.BooleanField(default=True)

    class Meta:
        db_table = 'ofertas'

    def __str__(self):
        return f"Oferta {self.producto.nombre} — {self.valor_descuento}"