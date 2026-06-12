from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',                    views.vista_dashboard,       name='index'),
    path('inventario/',         views.vista_inventario,      name='inventario'),
    path('productos/',          views.vista_productos_admin, name='productos'),
    path('productos/<int:pk>/edit/', views.vista_editar_producto, name='editar_producto'),
    path('productos/<int:pk>/toggle-activo/', views.vista_desactivar_producto, name='desactivar_producto'),
    path('pedidos/',            views.vista_pedidos_admin,   name='pedidos'),
    path('pedidos/<int:pedido_id>/rechazar/', views.vista_rechazar_pedido_admin, name='rechazar_pedido'),
    path('ofertas/',            views.vista_ofertas_admin,   name='ofertas'),
    path('ofertas/<int:pk>/edit/', views.vista_editar_oferta, name='editar_oferta'),
    path('ofertas/<int:pk>/toggle/', views.vista_desactivar_oferta, name='desactivar_oferta'),
    path('estadisticas/',       views.vista_estadisticas,    name='estadisticas'),
]