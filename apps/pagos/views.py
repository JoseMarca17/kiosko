import hashlib
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
import json

from .models import Transaccion, Comprobante, QRKiosko
from apps.pedidos.models import Pedido, EstadoPedido
from apps.usuarios.decorators import solo_admin


@login_required
def vista_pagar(request, pedido_id):
    """Muestra el QR activo y el formulario para subir comprobante"""
    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)

    if pedido.estado.nombre != 'pendiente_pago':
        return redirect('pedidos:detalle', pk=pedido_id)

    qr_activo = QRKiosko.objects.filter(activo=True).first()

    # Crear transacción si no existe
    transaccion, _ = Transaccion.objects.get_or_create(
        pedido=pedido,
        defaults={
            'qr_usado': qr_activo,
            'monto':    pedido.total,
            'estado':   'pendiente_validacion',
        }
    )

    if request.method == 'POST' and request.FILES.get('comprobante'):
        archivo = request.FILES['comprobante']

        # Hash para evitar duplicados
        contenido  = archivo.read()
        hash_img   = hashlib.sha256(contenido).hexdigest()
        archivo.seek(0)

        if Comprobante.objects.filter(hash_imagen=hash_img).exists():
            from django.contrib import messages
            messages.error(request, 'Este comprobante ya fue subido anteriormente.')
            return redirect('pagos:pagar', pedido_id=pedido_id)

        Comprobante.objects.create(
            transaccion = transaccion,
            imagen      = archivo,
            hash_imagen = hash_img,
        )

        # Cambiar estado del pedido
        estado_validacion = EstadoPedido.objects.get(nombre='pendiente_validacion')
        pedido.estado     = estado_validacion
        pedido.save()

        from django.contrib import messages
        messages.success(request, '¡Comprobante enviado! El kiosko lo validará en breve.')
        return redirect('pedidos:detalle', pk=pedido_id)

    return render(request, 'pagos/pagar.html', {
        'pedido':      pedido,
        'qr_activo':   qr_activo,
        'transaccion': transaccion,
    })


@solo_admin
@require_POST
def vista_validar_comprobante(request, transaccion_id):
    """Admin aprueba o rechaza un comprobante — llamado por JS del dashboard"""
    try:
        data       = json.loads(request.body)
        accion     = data.get('accion')  # 'aprobar' o 'rechazar'
        transaccion = get_object_or_404(Transaccion, pk=transaccion_id)

        if accion == 'aprobar':
            transaccion.estado          = 'aprobado'
            transaccion.validado_por    = request.user
            transaccion.fecha_validacion = timezone.now()
            transaccion.save()

            estado_pagado          = EstadoPedido.objects.get(nombre='pagado')
            transaccion.pedido.estado = estado_pagado
            transaccion.pedido.save()

            # El trigger de MySQL descuenta el stock automáticamente
            # pero si prefieres manejarlo en Django:
            for detalle in transaccion.pedido.detalles.all():
                inv = detalle.producto.inventario
                inv.stock_actual -= detalle.cantidad
                inv.save()

            return JsonResponse({'ok': True, 'mensaje': 'Pago aprobado ✓'})

        elif accion == 'rechazar':
            transaccion.estado           = 'rechazado'
            transaccion.validado_por     = request.user
            transaccion.fecha_validacion = timezone.now()
            transaccion.notas_validacion = data.get('motivo', '')
            transaccion.save()

            estado_cancelado           = EstadoPedido.objects.get(nombre='cancelado')
            transaccion.pedido.estado  = estado_cancelado
            transaccion.pedido.cancelado = True
            transaccion.pedido.save()

            return JsonResponse({'ok': True, 'mensaje': 'Pago rechazado'})

        return JsonResponse({'error': 'Acción inválida'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@solo_admin
def vista_cambiar_estado_pedido(request, pedido_id):
    """Admin cambia estado: preparando → listo → entregado"""
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    nuevo_estado = request.POST.get('estado')

    estados_validos = ['preparando', 'listo', 'entregado']
    if nuevo_estado in estados_validos:
        pedido.estado = EstadoPedido.objects.get(nombre=nuevo_estado)
        pedido.save()
        return JsonResponse({'ok': True, 'estado': nuevo_estado})

    return JsonResponse({'error': 'Estado inválido'}, status=400)