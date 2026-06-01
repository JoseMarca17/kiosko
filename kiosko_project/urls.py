from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('',            include('apps.catalogo.urls')),
    path('usuarios/',   include('apps.usuarios.urls')),
    path('pedidos/',    include('apps.pedidos.urls')),
    path('pagos/',      include('apps.pagos.urls')),
    path('dashboard/',  include('apps.dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)