from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta
import json

from apps.usuarios.decorators import solo_admin
from apps.catalogo.models import Producto, Categoria, Inventario
from apps.pedidos.models import Pedido, EstadoPedido, DetallePedido
from apps.pagos.models import Transaccion, QRKiosko


@solo_admin
def vista_dashboard(request):
    hoy      = timezone.now().date()
    hace7    = hoy - timedelta(days=6)

    # Tarjetas de resumen
    ventas_hoy     = Pedido.objects.filter(
        fecha_pedido__date=hoy,
        estado__nombre__in=['pagado','preparando','listo','entregado'],
        cancelado=False
    ).aggregate(total=Sum('total'))['total'] or 0

    pedidos_hoy    = Pedido.objects.filter(
        fecha_pedido__date=hoy, cancelado=False
    ).exclude(estado__nombre='cancelado').count()

    pendientes     = Transaccion.objects.filter(estado='pendiente_validacion').count()

    stock_bajo     = Inventario.objects.filter(
        stock_actual__lte=F('stock_minimo')
    ).count()

    # Gráfica ventas 7 días
    ventas_semana  = []
    labels_semana  = []
    for i in range(6, -1, -1):
        dia   = hoy - timedelta(days=i)
        total = Pedido.objects.filter(
            fecha_pedido__date=dia,
            estado__nombre__in=['pagado','preparando','listo','entregado'],
            cancelado=False
        ).aggregate(t=Sum('total'))['t'] or 0
        ventas_semana.append(float(total))
        labels_semana.append(dia.strftime('%d/%m'))

    # Top 5 productos
    top_productos  = DetallePedido.objects.filter(
        pedido__cancelado=False,
        pedido__estado__nombre__in=['pagado','preparando','listo','entregado']
    ).values('producto__nombre').annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')[:5]

    # Comprobantes pendientes de validar
    comprobantes_pendientes = Transaccion.objects.filter(
        estado='pendiente_validacion'
    ).select_related('pedido', 'pedido__usuario').prefetch_related('comprobantes')[:20]

    return render(request, 'dashboard/index.html', {
        'ventas_hoy':              ventas_hoy,
        'pedidos_hoy':             pedidos_hoy,
        'pendientes':              pendientes,
        'stock_bajo':              stock_bajo,
        'labels_semana':           json.dumps(labels_semana),
        'ventas_semana':           json.dumps(ventas_semana),
        'top_productos':           list(top_productos),
        'labels_top':              json.dumps([p['producto__nombre'] for p in top_productos]),
        'datos_top':               json.dumps([p['total_vendido'] for p in top_productos]),
        'comprobantes_pendientes': comprobantes_pendientes,
    })


@solo_admin
def vista_inventario(request):
    inventario = Inventario.objects.select_related('producto__categoria')\
                                   .order_by('stock_actual')

    if request.method == 'POST':
        prod_id   = request.POST.get('producto_id')
        nuevo_stock = int(request.POST.get('stock', 0))
        inv = get_object_or_404(Inventario, producto_id=prod_id)
        inv.stock_actual = nuevo_stock
        inv.save()
        return JsonResponse({'ok': True})

    return render(request, 'dashboard/inventario.html', {'inventario': inventario})


@solo_admin
def vista_productos_admin(request):
    """CRUD de productos"""
    from apps.catalogo.forms import ProductoForm
    productos = Producto.objects.select_related('categoria').order_by('-fecha_creacion')

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            # Crear inventario inicial
            Inventario.objects.get_or_create(
                producto=producto,
                defaults={'stock_actual': request.POST.get('stock_inicial', 0)}
            )
            from django.contrib import messages
            messages.success(request, f'Producto "{producto.nombre}" creado.')
            return redirect('dashboard:productos')
    else:
        form = ProductoForm()

    return render(request, 'dashboard/productos.html', {
        'productos': productos,
        'form':      form,
    })


@solo_admin
def vista_editar_producto(request, pk):
    from apps.catalogo.forms import ProductoForm
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, 'Producto actualizado.')
            return redirect('dashboard:productos')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'dashboard/editar_producto.html', {
        'form':     form,
        'producto': producto,
    })


@solo_admin
def vista_pedidos_admin(request):
    estado_filtro = request.GET.get('estado', '')
    pedidos = Pedido.objects.select_related('estado', 'usuario')\
                            .order_by('-fecha_pedido')
    if estado_filtro:
        pedidos = pedidos.filter(estado__nombre=estado_filtro)

    estados = EstadoPedido.objects.all()
    return render(request, 'dashboard/pedidos.html', {
        'pedidos':        pedidos,
        'estados':        estados,
        'estado_filtro':  estado_filtro,
    })


@solo_admin
def vista_estadisticas(request):
    # Productos más y menos vendidos
    stats_productos = DetallePedido.objects.filter(
        pedido__cancelado=False,
        pedido__estado__nombre__in=['pagado','preparando','listo','entregado']
    ).values(
        'producto__id', 'producto__nombre', 'producto__categoria__nombre'
    ).annotate(
        unidades=Sum('cantidad'),
        ingresos=Sum('subtotal')
    ).order_by('-unidades')

    # Ventas por categoría
    ventas_cat = DetallePedido.objects.filter(
        pedido__cancelado=False,
        pedido__estado__nombre__in=['pagado','preparando','listo','entregado']
    ).values('producto__categoria__nombre').annotate(
        total=Sum('subtotal')
    ).order_by('-total')

    # Ingresos por mes (últimos 6 meses)
    hoy     = timezone.now().date()
    meses   = []
    ingresos_mes = []
    for i in range(5, -1, -1):
        mes   = hoy.replace(day=1) - timedelta(days=i*30)
        total = Pedido.objects.filter(
            fecha_pedido__year=mes.year,
            fecha_pedido__month=mes.month,
            cancelado=False,
            estado__nombre__in=['pagado','preparando','listo','entregado']
        ).aggregate(t=Sum('total'))['t'] or 0
        meses.append(mes.strftime('%b %Y'))
        ingresos_mes.append(float(total))

    return render(request, 'dashboard/estadisticas.html', {
        'stats_productos':   list(stats_productos),
        'ventas_cat':        list(ventas_cat),
        'labels_meses':      json.dumps(meses),
        'ingresos_mes':      json.dumps(ingresos_mes),
        'labels_cat':        json.dumps([v['producto__categoria__nombre'] for v in ventas_cat]),
        'datos_cat':         json.dumps([float(v['total']) for v in ventas_cat]),
    })