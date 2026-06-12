from apps.pedidos.models import Pedido

def pedidos_pendientes(request):
    if request.user and request.user.is_authenticated:
        pedidos_pago = Pedido.objects.filter(usuario=request.user, estado__nombre='pendiente_pago').order_by('-fecha_pedido')
        pedidos_val = Pedido.objects.filter(usuario=request.user, estado__nombre='pendiente_validacion').order_by('-fecha_pedido')
        return {
            'pedidos_pendientes_pago': pedidos_pago,
            'pedidos_pendientes_validacion': pedidos_val,
        }
    return {
        'pedidos_pendientes_pago': [],
        'pedidos_pendientes_validacion': [],
    }
