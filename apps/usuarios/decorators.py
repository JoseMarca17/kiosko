from django.shortcuts import redirect
from functools import wraps


def solo_admin(view_func):
    """Solo admin o staff_kiosko pueden acceder"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        if not (request.user.es_admin or request.user.es_staff_kiosko):
            return redirect('catalogo:index')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_requerido_ajax(view_func):
    """Para vistas llamadas por JS — devuelve JSON 401"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.http import JsonResponse
            return JsonResponse({'error': 'no_auth'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper