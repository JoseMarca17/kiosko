from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('checkout/',                       views.vista_checkout,       name='checkout'),
    path('mis-pedidos/',                    views.vista_mis_pedidos,    name='mis_pedidos'),
    path('detalle/<int:pk>/',               views.vista_detalle_pedido, name='detalle'),
    path('cancelar/<int:pk>/',              views.vista_cancelar_pedido,name='cancelar'),
]