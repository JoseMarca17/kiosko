from django.db import models

class Categoria(models.Model):
    id          = models.AutoField(primary_key=True, db_column='id_categoria')
    nombre      = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    icono_url   = models.CharField(max_length=255, null=True, blank=True)
    orden       = models.IntegerField(default=0)
    activo      = models.BooleanField(default=True)

    class Meta:
        db_table = 'categorias'
        ordering = ['orden']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    id          = models.AutoField(primary_key=True, db_column='id_producto')
    nombre      = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    categoria   = models.ForeignKey(Categoria, on_delete=models.PROTECT, db_column='id_categoria')
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    imagen      = models.ImageField(upload_to='productos/', blank=True, null=True, db_column='imagen_url')
    destacado   = models.BooleanField(default=False)
    activo      = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'productos'

    def __str__(self):
        return self.nombre

    def get_oferta_activa(self):
        """Retorna el objeto Oferta activo para el producto, si existe"""
        from django.utils import timezone
        ofertas_activas = self.ofertas.filter(
            activo=True,
            fecha_inicio__lte=timezone.now(),
            fecha_fin__gte=timezone.now()
        )
        for o in ofertas_activas:
            if o.limite_cantidad is None or o.cantidad_vendida < o.limite_cantidad:
                return o
        return None

    def precio_actual(self):
        """Retorna el precio con descuento si hay oferta activa"""
        oferta = self.get_oferta_activa()
        if not oferta:
            return self.precio_base
        if oferta.tipo_descuento == 'porcentaje':
            return self.precio_base * (1 - oferta.valor_descuento / 100)
        return max(self.precio_base - oferta.valor_descuento, 0)


class Inventario(models.Model):
    id                  = models.AutoField(primary_key=True, db_column='id_inventario')
    producto            = models.OneToOneField(Producto, on_delete=models.CASCADE, db_column='id_producto', related_name='inventario')
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
    id              = models.AutoField(primary_key=True, db_column='id_oferta')
    producto        = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto', related_name='ofertas')
    tipo_descuento  = models.CharField(max_length=20, choices=TIPO_CHOICES)
    valor_descuento = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion     = models.CharField(max_length=255, null=True, blank=True)
    fecha_inicio    = models.DateTimeField()
    fecha_fin       = models.DateTimeField()
    limite_cantidad = models.IntegerField(null=True, blank=True)
    cantidad_vendida = models.IntegerField(default=0)
    activo          = models.BooleanField(default=True)

    class Meta:
        db_table = 'ofertas'

    def __str__(self):
        return f"Oferta {self.producto.nombre} — {self.valor_descuento}"