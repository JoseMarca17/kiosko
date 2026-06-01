from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('',                              views.vista_inicio,              name='index'),
    path('catalogo/',                     views.vista_catalogo,            name='catalogo'),
    path('catalogo/producto/<int:pk>/',   views.vista_detalle_producto,    name='detalle'),
    path('api/categoria/<int:cat_id>/',   views.api_productos_categoria,   name='api_categoria'),
    path('nosotros/',                     views.vista_nosotros,            name='nosotros'),
]