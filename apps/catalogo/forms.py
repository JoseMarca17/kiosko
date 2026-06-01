from django import forms
from .models import Producto, Oferta


class ProductoForm(forms.ModelForm):
    class Meta:
        model  = Producto
        fields = ['nombre', 'descripcion', 'categoria', 'precio_base',
                  'imagen', 'destacado', 'activo']
        labels = {
            'nombre':      'Nombre del producto',
            'descripcion': 'Descripción',
            'categoria':   'Categoría',
            'precio_base': 'Precio base (Bs.)',
            'imagen':      'Imagen',
            'destacado':   'Mostrar como destacado',
            'activo':      'Producto activo',
        }
        widgets = {
            'nombre':      forms.TextInput(attrs={'placeholder': 'Ej: Salteña de pollo'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'precio_base': forms.NumberInput(attrs={'step': '0.50', 'min': '0'}),
        }


class OfertaForm(forms.ModelForm):
    class Meta:
        model  = Oferta
        fields = ['producto', 'tipo_descuento', 'valor_descuento',
                  'descripcion', 'fecha_inicio', 'fecha_fin', 'activo']
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_fin':    forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }