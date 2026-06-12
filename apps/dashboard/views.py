from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta, datetime, time
import json

from apps.usuarios.decorators import solo_admin
from apps.catalogo.models import Producto, Categoria, Inventario, Oferta
from apps.pedidos.models import Pedido, EstadoPedido, DetallePedido
from apps.pagos.models import Transaccion, QRKiosko


@solo_admin
def vista_dashboard(request):
    local_now = timezone.localtime(timezone.now())
    hoy_local = local_now.date()

    # Tarjetas de resumen (usando rangos exactos de fecha/hora locales)
    start_of_today = timezone.make_aware(datetime.combine(hoy_local, time.min))
    end_of_today = timezone.make_aware(datetime.combine(hoy_local, time.max))

    ventas_hoy     = Pedido.objects.filter(
        fecha_pedido__gte=start_of_today,
        fecha_pedido__lte=end_of_today,
        estado__nombre__in=['pagado','preparando','listo','entregado'],
        cancelado=False
    ).aggregate(total=Sum('total'))['total'] or 0

    pedidos_hoy    = Pedido.objects.filter(
        fecha_pedido__gte=start_of_today,
        fecha_pedido__lte=end_of_today,
        cancelado=False
    ).exclude(estado__nombre='cancelado').count()

    pendientes     = Transaccion.objects.filter(estado='pendiente_validacion').count()

    stock_bajo     = Inventario.objects.filter(
        stock_actual__lte=F('stock_minimo')
    ).count()

    # Gráfica ventas 7 días (usando rangos exactos de fecha/hora locales)
    ventas_semana  = []
    labels_semana  = []
    for i in range(6, -1, -1):
        dia   = hoy_local - timedelta(days=i)
        start_of_dia = timezone.make_aware(datetime.combine(dia, time.min))
        end_of_dia = timezone.make_aware(datetime.combine(dia, time.max))
        
        total = Pedido.objects.filter(
            fecha_pedido__gte=start_of_dia,
            fecha_pedido__lte=end_of_dia,
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
        'today':                   local_now,
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

    from django.db.models import F
    total_productos = inventario.count()
    agotados        = inventario.filter(stock_actual=0).count()
    stock_bajo      = inventario.filter(stock_actual__lte=F('stock_minimo'), stock_actual__gt=0).count()
    saludables      = inventario.filter(stock_actual__gt=F('stock_minimo')).count()
    categorias      = Categoria.objects.all().order_by('nombre')

    return render(request, 'dashboard/inventario.html', {
        'inventario':      inventario,
        'total_productos': total_productos,
        'agotados':        agotados,
        'stock_bajo':      stock_bajo,
        'saludables':      saludables,
        'categorias':      categorias,
    })


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

    categorias = Categoria.objects.all().order_by('nombre')

    return render(request, 'dashboard/productos.html', {
        'productos':  productos,
        'form':       form,
        'categorias': categorias,
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
def vista_desactivar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.activo = not producto.activo
    producto.save()
    from django.contrib import messages
    estado = "activado" if producto.activo else "desactivado (dado de baja)"
    messages.success(request, f'Producto "{producto.nombre}" {estado}.')
    return redirect('dashboard:productos')


@solo_admin
def vista_pedidos_admin(request):
    tab = request.GET.get('tab', 'activos')  # activos, completados, rechazados
    rango_fecha = request.GET.get('fecha', 'todo')  # hoy, semana, mes, todo
    estado_filtro = request.GET.get('estado', '')

    pedidos = Pedido.objects.select_related('estado', 'usuario')\
                            .prefetch_related('detalles__producto', 'transaccion__comprobantes')\
                            .order_by('-fecha_pedido')

    # Filtro por tab
    if tab == 'activos':
        pedidos = pedidos.filter(estado__nombre__in=['pendiente_pago', 'pendiente_validacion', 'pagado', 'preparando', 'listo'])
    elif tab == 'completados':
        pedidos = pedidos.filter(estado__nombre='entregado')
    elif tab == 'rechazados':
        pedidos = pedidos.filter(estado__nombre='cancelado')

    # Filtro por rango de fecha
    if rango_fecha != 'todo':
        from datetime import datetime, time
        local_now = timezone.localtime(timezone.now())
        if rango_fecha == 'hoy':
            inicio = timezone.make_aware(datetime.combine(local_now.date(), time.min))
            pedidos = pedidos.filter(fecha_pedido__gte=inicio)
        elif rango_fecha == 'semana':
            inicio = timezone.make_aware(datetime.combine(local_now.date() - timedelta(days=7), time.min))
            pedidos = pedidos.filter(fecha_pedido__gte=inicio)
        elif rango_fecha == 'mes':
            inicio = timezone.make_aware(datetime.combine(local_now.date() - timedelta(days=30), time.min))
            pedidos = pedidos.filter(fecha_pedido__gte=inicio)

    if estado_filtro:
        pedidos = pedidos.filter(estado__nombre=estado_filtro)

    # Calcular estadísticas del período filtrado
    stats = {
        'total_pedidos': pedidos.count(),
        'total_monto':   pedidos.aggregate(total=Sum('total'))['total'] or 0.00,
    }

    estados = EstadoPedido.objects.all()
    return render(request, 'dashboard/pedidos.html', {
        'pedidos':        pedidos,
        'estados':        estados,
        'estado_filtro':  estado_filtro,
        'tab':            tab,
        'rango_fecha':    rango_fecha,
        'stats':          stats,
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
    from datetime import datetime
    hoy_local = timezone.localtime(timezone.now()).date()
    meses   = []
    ingresos_mes = []
    anio = hoy_local.year
    mes_num = hoy_local.month

    for i in range(5, -1, -1):
        m = mes_num - i
        y = anio
        while m <= 0:
            m += 12
            y -= 1
            
        inicio_mes = timezone.make_aware(datetime(y, m, 1, 0, 0, 0))
        if m == 12:
            fin_mes = timezone.make_aware(datetime(y + 1, 1, 1, 0, 0, 0))
        else:
            fin_mes = timezone.make_aware(datetime(y, m + 1, 1, 0, 0, 0))
            
        total = Pedido.objects.filter(
            fecha_pedido__gte=inicio_mes,
            fecha_pedido__lt=fin_mes,
            cancelado=False,
            estado__nombre__in=['pagado','preparando','listo','entregado']
        ).aggregate(t=Sum('total'))['t'] or 0
        
        nombres_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        label = f"{nombres_meses[m-1]} {y}"
        
        meses.append(label)
        ingresos_mes.append(float(total))

    return render(request, 'dashboard/estadisticas.html', {
        'stats_productos':   list(stats_productos),
        'ventas_cat':        list(ventas_cat),
        'labels_meses':      json.dumps(meses),
        'ingresos_mes':      json.dumps(ingresos_mes),
        'labels_cat':        json.dumps([v['producto__categoria__nombre'] for v in ventas_cat]),
        'datos_cat':         json.dumps([float(v['total']) for v in ventas_cat]),
    })


@solo_admin
def vista_ofertas_admin(request):
    from apps.catalogo.forms import OfertaForm
    ofertas = Oferta.objects.select_related('producto__categoria').order_by('-fecha_inicio')
    categorias = Categoria.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        form = OfertaForm(request.POST)
        if form.is_valid():
            oferta = form.save()
            from django.contrib import messages
            messages.success(request, f'Oferta creada para el producto "{oferta.producto.nombre}".')
            return redirect('dashboard:ofertas')
    else:
        form = OfertaForm()
        
    return render(request, 'dashboard/ofertas.html', {
        'ofertas':    ofertas,
        'form':       form,
        'categorias': categorias,
        'now':        timezone.now(),
    })


@solo_admin
def vista_editar_oferta(request, pk):
    from apps.catalogo.forms import OfertaForm
    oferta = get_object_or_404(Oferta, pk=pk)
    
    if request.method == 'POST':
        form = OfertaForm(request.POST, instance=oferta)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, 'Oferta actualizada con éxito.')
            return redirect('dashboard:ofertas')
    else:
        form = OfertaForm(instance=oferta)
        
    return render(request, 'dashboard/editar_oferta.html', {
        'form':   form,
        'oferta': oferta,
    })


@solo_admin
def vista_desactivar_oferta(request, pk):
    oferta = get_object_or_404(Oferta, pk=pk)
    oferta.activo = not oferta.activo
    oferta.save()
    
    from django.contrib import messages
    estado = "activada" if oferta.activo else "desactivada"
    messages.success(request, f'La oferta del producto "{oferta.producto.nombre}" fue {estado}.')
    return redirect('dashboard:ofertas')


@solo_admin
def vista_rechazar_pedido_admin(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        if pedido.estado.nombre == 'entregado':
            return JsonResponse({'error': 'No se puede rechazar un pedido ya entregado.'}, status=400)

        data = {}
        try:
            if request.body:
                data = json.loads(request.body)
        except Exception:
            pass

        motivo = data.get('motivo') or request.POST.get('motivo') or 'Rechazado por el administrador'
        
        from django.db import transaction
        with transaction.atomic():
            pedido.cancelado = True
            pedido.fecha_cancelacion = timezone.now()
            pedido.motivo_cancelacion = motivo
            pedido.estado = EstadoPedido.objects.get(nombre='cancelado')
            pedido.save()
            
            # Revertir stock e incremento de ofertas asociadas
            for detalle in pedido.detalles.all():
                inv = detalle.producto.inventario
                inv.stock_actual += detalle.cantidad
                inv.save()
                
                if detalle.oferta:
                    o = detalle.oferta
                    o.cantidad_vendida = max(o.cantidad_vendida - detalle.cantidad, 0)
                    o.save()
            
            # Rechazar transacciones asociadas
            if hasattr(pedido, 'transaccion'):
                t = pedido.transaccion
                t.estado = 'rechazado'
                t.validado_por = request.user
                t.fecha_validacion = timezone.now()
                t.notas_validacion = motivo
                t.save()
                
        return JsonResponse({'ok': True, 'mensaje': 'Pedido rechazado/cancelado con éxito.'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)