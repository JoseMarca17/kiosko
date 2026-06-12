from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
import json

from .models import Pedido, DetallePedido, EstadoPedido
from apps.catalogo.models import Producto


@login_required
def vista_checkout(request):
    """Recibe el carrito desde el frontend y crea el pedido"""
    if request.method == 'POST':
        try:
            data  = json.loads(request.body)
            items = data.get('items', [])

            if not items:
                return JsonResponse({'error': 'Carrito vacío'}, status=400)

            with transaction.atomic():
                # Calcular totales y validar stock
                subtotal = 0
                detalles = []
                for item in items:
                    producto = get_object_or_404(Producto, pk=item['id'], activo=True)
                    if producto.inventario.stock_actual < item['cantidad']:
                        return JsonResponse({
                            'error': f'Stock insuficiente para {producto.nombre}'
                        }, status=400)

                    # Verificar límite de la oferta
                    ofertas_activas = producto.ofertas.filter(
                        activo=True,
                        fecha_inicio__lte=timezone.now(),
                        fecha_fin__gte=timezone.now()
                    )
                    oferta_aplicada = None
                    for o in ofertas_activas:
                        if o.limite_cantidad is None or o.cantidad_vendida < o.limite_cantidad:
                            oferta_aplicada = o
                            break

                    if oferta_aplicada and oferta_aplicada.limite_cantidad is not None:
                        restante = oferta_aplicada.limite_cantidad - oferta_aplicada.cantidad_vendida
                        if item['cantidad'] > restante:
                            return JsonResponse({
                                'error': f'Solo quedan {restante} unidades en oferta para {producto.nombre}.'
                            }, status=400)

                    precio   = float(producto.precio_actual())
                    sub_item = precio * item['cantidad']
                    subtotal += sub_item
                    detalles.append({
                        'producto':          producto,
                        'oferta':            oferta_aplicada,
                        'cantidad':          item['cantidad'],
                        'precio_unitario':   precio,
                        'subtotal':          sub_item,
                        'notas':             item.get('notes', ''),
                    })

                estado_inicial = EstadoPedido.objects.get(nombre='pendiente_pago')

                pedido = Pedido.objects.create(
                    usuario          = request.user,
                    estado           = estado_inicial,
                    subtotal         = subtotal,
                    total            = subtotal,
                    notas_especiales = data.get('notas', ''),
                    fecha_estimada_retiro = timezone.now() + timezone.timedelta(minutes=20),
                )

                for d in detalles:
                    DetallePedido.objects.create(
                        pedido           = pedido,
                        producto         = d['producto'],
                        oferta           = d['oferta'],
                        cantidad         = d['cantidad'],
                        precio_unitario  = d['precio_unitario'],
                        subtotal         = d['subtotal'],
                        notas            = d['notas'],
                    )
                    # Descontar stock inmediatamente
                    inv = d['producto'].inventario
                    inv.stock_actual = max(inv.stock_actual - d['cantidad'], 0)
                    inv.save()

                    # Incrementar la cantidad vendida en la oferta
                    if d['oferta']:
                        o = d['oferta']
                        o.cantidad_vendida += d['cantidad']
                        o.save()

            return JsonResponse({'ok': True, 'pedido_id': pedido.id,
                                 'codigo': pedido.codigo_pedido})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # GET — mostrar página de checkout
    return render(request, 'pedidos/checkout.html')


@login_required
def vista_mis_pedidos(request):
    pedidos = Pedido.objects.filter(
        usuario=request.user
    ).select_related('estado').order_by('-fecha_pedido')

    return render(request, 'pedidos/mis_pedidos.html', {'pedidos': pedidos})


@login_required
def vista_detalle_pedido(request, pk):
    pedido   = get_object_or_404(Pedido, pk=pk, usuario=request.user)
    detalles = pedido.detalles.select_related('producto').all()
    return render(request, 'pedidos/detalle_pedido.html', {
        'pedido':   pedido,
        'detalles': detalles,
    })


@login_required
def vista_cancelar_pedido(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk, usuario=request.user)
    if pedido.estado.nombre not in ('pendiente_pago', 'pendiente_validacion'):
        messages.error(request, 'Este pedido ya no puede cancelarse.')
        return redirect('pedidos:detalle', pk=pk)

    with transaction.atomic():
        pedido.cancelado         = True
        pedido.fecha_cancelacion = timezone.now()
        pedido.motivo_cancelacion = request.POST.get('motivo', 'Cancelado por el usuario')
        estado_cancelado         = EstadoPedido.objects.get(nombre='cancelado')
        pedido.estado            = estado_cancelado
        pedido.save()

        # Revertir stock e incremento de ofertas asociadas
        for detalle in pedido.detalles.all():
            # Restaurar stock
            inv = detalle.producto.inventario
            inv.stock_actual += detalle.cantidad
            inv.save()

            # Revertir oferta
            if detalle.oferta:
                o = detalle.oferta
                o.cantidad_vendida = max(o.cantidad_vendida - detalle.cantidad, 0)
                o.save()

    messages.success(request, 'Pedido cancelado.')
    return redirect('pedidos:mis_pedidos')