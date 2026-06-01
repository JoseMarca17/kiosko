from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',                    views.vista_dashboard,       name='index'),
    path('inventario/',         views.vista_inventario,      name='inventario'),
    path('productos/',          views.vista_productos_admin, name='productos'),
    path('productos/<int:pk>/edit/', views.vista_editar_producto, name='editar_producto'),
    path('pedidos/',            views.vista_pedidos_admin,   name='pedidos'),
    path('estadisticas/',       views.vista_estadisticas,    name='estadisticas'),
]