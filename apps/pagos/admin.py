from django.contrib import admin

# Register your models here.
from .models import QRKiosko, Transaccion, Comprobante

@admin.register(QRKiosko)
class QRKioskoAdmin(admin.ModelAdmin):
    list_display = ('banco', 'titular', 'numero_cuenta', 'activo', 'fecha_registro')
    list_filter = ('activo', 'banco')
    search_fields = ('banco', 'titular', 'numero_cuenta')

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'qr_usado', 'monto', 'estado', 'fecha_transaccion', 'validado_por')
    list_filter = ('estado', 'fecha_transaccion')
    search_fields = ('pedido__codigo_pedido', 'qr_usado__banco', 'qr_usado__titular')

@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ('transaccion', 'monto_detectado', 'hash_imagen', 'fecha_subida', 'validado')
    list_filter = ('validado', 'fecha_subida')
