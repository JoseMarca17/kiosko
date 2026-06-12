from django.db import models

class VentasDiarias(models.Model):
    fecha = models.DateField(unique=True)
    total_ventas = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_pedidos = models.IntegerField(default=0)
    ticket_promedio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    producto_top = models.ForeignKey('catalogo.Producto', on_delete=models.SET_NULL, null=True, blank=True, db_column='id_producto_top')

    class Meta:
        db_table = 'ventas_diarias'
        verbose_name_plural = 'ventas_diarias'

    def __str__(self):
        return f"Ventas {self.fecha} — Total: {self.total_ventas}"


class ProductosMasVendidosView(models.Model):
    id_producto = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100)
    unidades_vendidas = models.IntegerField()
    ingresos_totales = models.DecimalField(max_digits=12, decimal_places=2)
    veces_pedido = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'v_productos_mas_vendidos'

    def __str__(self):
        return f"{self.nombre} ({self.unidades_vendidas} vendidos)"
