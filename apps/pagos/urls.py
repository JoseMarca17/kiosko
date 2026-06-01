from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('pagar/<int:pedido_id>/',          views.vista_pagar,                 name='pagar'),
    path('validar/<int:transaccion_id>/',   views.vista_validar_comprobante,   name='validar'),
    path('estado/<int:pedido_id>/',         views.vista_cambiar_estado_pedido, name='cambiar_estado'),
]