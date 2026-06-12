from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Producto, Categoria, Oferta
from django.utils import timezone
from django.db.models import Q, F


def vista_inicio(request):
    """Página principal con banner, ofertas y productos por categoría"""
    categorias  = Categoria.objects.filter(activo=True).order_by('orden')
    # Ofertas activas para el banner (no agotadas)
    ofertas     = Oferta.objects.filter(
        activo=True,
        fecha_inicio__lte=timezone.now(),
        fecha_fin__gte=timezone.now()
    ).filter(
        Q(limite_cantidad__isnull=True) | Q(cantidad_vendida__lt=F('limite_cantidad'))
    ).select_related('producto')[:5]
    # Productos destacados
    destacados  = Producto.objects.filter(activo=True, destacado=True)\
                                  .select_related('categoria')[:8]
    # 4 productos por categoría para preview
    cats_preview = []
    for cat in categorias:
        prods = Producto.objects.filter(activo=True, categoria=cat)\
                                .prefetch_related('ofertas')[:4]
        if prods.exists():
            cats_preview.append({'categoria': cat, 'productos': prods})

    return render(request, 'catalogo/inicio.html', {
        'categorias':   categorias,
        'ofertas':      ofertas,
        'destacados':   destacados,
        'cats_preview': cats_preview,
    })


def vista_catalogo(request):
    """Catálogo completo con filtro por categoría y búsqueda"""
    categorias = Categoria.objects.filter(activo=True).order_by('orden')
    cat_id     = request.GET.get('categoria')
    busqueda   = request.GET.get('q', '').strip()

    productos = Producto.objects.filter(activo=True).select_related('categoria')

    if cat_id:
        productos = productos.filter(categoria_id=cat_id)
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | Q(descripcion__icontains=busqueda)
        )

    cat_activa = None
    if cat_id:
        try:
            cat_activa = Categoria.objects.get(id=cat_id)
        except Categoria.DoesNotExist:
            pass

    return render(request, 'catalogo/catalogo.html', {
        'productos':   productos,
        'categorias':  categorias,
        'cat_activa':  cat_activa,
        'busqueda':    busqueda,
    })


def vista_detalle_producto(request, pk):
    """Detalle individual del producto"""
    producto   = get_object_or_404(Producto, pk=pk, activo=True)
    relacionados = Producto.objects.filter(
        activo=True,
        categoria=producto.categoria
    ).exclude(pk=pk)[:4]

    oferta_activa = producto.ofertas.filter(
        activo=True,
        fecha_inicio__lte=timezone.now(),
        fecha_fin__gte=timezone.now()
    ).filter(
        Q(limite_cantidad__isnull=True) | Q(cantidad_vendida__lt=F('limite_cantidad'))
    ).first()

    return render(request, 'catalogo/detalle_producto.html', {
        'producto':      producto,
        'relacionados':  relacionados,
        'oferta_activa': oferta_activa,
        'precio_final':  producto.precio_actual(),
    })

def vista_nosotros(request):
    """Página institucional Sobre Nosotros"""
    return render(request, 'catalogo/nosotros.html')

def api_productos_categoria(request, cat_id):
    """API para cargar más productos de una categoría (paginación simple)"""
    page  = int(request.GET.get('page', 1))
    limit = 10
    offset = (page - 1) * limit

    productos = Producto.objects.filter(
        activo=True, categoria_id=cat_id
    ).values('id', 'nombre', 'precio_base', 'imagen')[offset:offset + limit]

    total = Producto.objects.filter(activo=True, categoria_id=cat_id).count()

    data = []
    for p in productos:
        img = p['imagen']
        data.append({
            'id':     p['id'],
            'nombre': p['nombre'],
            'precio': float(p['precio_base']),
            'imagen': f"/media/{img}" if img else None,
            'url':    f"/catalogo/producto/{p['id']}/",
        })

    return JsonResponse({'productos': data, 'total': total, 'page': page})