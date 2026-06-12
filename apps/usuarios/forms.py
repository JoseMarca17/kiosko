from django import forms
from .models import Usuario


class LoginForm(forms.Form):
    email    = forms.EmailField(label='Correo electrónico',
                                widget=forms.EmailInput(attrs={'placeholder': 'tu@correo.com'}))
    password = forms.CharField(label='Contraseña',
                               widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}))


class RegistroForm(forms.ModelForm):
    password  = forms.CharField(label='Contraseña',
                                widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}),
                                min_length=6)
    password2 = forms.CharField(label='Confirmar contraseña',
                                widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}))

    class Meta:
        model  = Usuario
        fields = ['nombre_completo', 'email', 'telefono']
        labels = {
            'nombre_completo':   'Nombre completo',
            'email':             'Correo electrónico',
            'telefono':          'Teléfono (opcional)',
        }
        widgets = {
            'nombre_completo':   forms.TextInput(attrs={'placeholder': 'Tu nombre completo'}),
            'email':             forms.EmailInput(attrs={'placeholder': 'tu@correo.com'}),
            'telefono':          forms.TextInput(attrs={'placeholder': '+591 7xxxxxxx'}),
        }

    def clean(self):
        cd = super().clean()
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('Las contraseñas no coinciden.')
        if Usuario.objects.filter(email=cd.get('email')).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo.')
        return cd