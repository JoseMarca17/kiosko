from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegistroForm


def vista_login(request):
    if request.user.is_authenticated:
        return redirect('catalogo:index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email    = form.cleaned_data['email']
            password = form.cleaned_data['password']
            from .models import Usuario
            try:
                user_obj = Usuario.objects.get(email=email)
                user = authenticate(request, username=email, password=password)
                if user:
                    login(request, user)
                    from django.utils import timezone
                    user.last_login = timezone.now()
                    user.save(update_fields=['last_login'])
                    next_url = request.GET.get('next', '/')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Contraseña incorrecta.')
            except Usuario.DoesNotExist:
                messages.error(request, 'No existe una cuenta con ese correo.')
    else:
        form = LoginForm()
    
    return render(request, 'usuarios/login.html', {'form': form})


def vista_registro(request):
    if request.user.is_authenticated:
        return redirect('catalogo:index')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            # Rol estudiante por defecto
            from .models import Rol
            try:
                user.rol = Rol.objects.get(nombre='estudiante')
            except Rol.DoesNotExist:
                pass
            user.save()
            messages.success(request, '¡Cuenta creada! Ya puedes iniciar sesión.')
            return redirect('usuarios:login')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


def vista_logout(request):
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('usuarios:login')