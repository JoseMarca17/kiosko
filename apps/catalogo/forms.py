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
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ej: Salteña de pollo',
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-xs focus:outline-none focus:border-[#2355a0] focus:bg-white transition-all text-gray-800 placeholder-gray-400'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Escribe una breve descripción del producto...',
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-xs focus:outline-none focus:border-[#2355a0] focus:bg-white transition-all text-gray-800 placeholder-gray-400'
            }),
            'categoria': forms.Select(attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-xs focus:outline-none focus:border-[#2355a0] focus:bg-white transition-all text-gray-800'
            }),
            'precio_base': forms.NumberInput(attrs={
                'step': '0.50',
                'min': '0',
                'placeholder': '0.00',
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-xs focus:outline-none focus:border-[#2355a0] focus:bg-white transition-all text-gray-800 placeholder-gray-400'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'w-full text-xs text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-blue-50 file:text-[#2355a0] hover:file:bg-blue-100 transition-all cursor-pointer'
            }),
            'destacado': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-[#2355a0] focus:ring-[#2355a0] h-4 w-4 transition-all'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-[#2355a0] focus:ring-[#2355a0] h-4 w-4 transition-all'
            }),
        }


class OfertaForm(forms.ModelForm):
    class Meta:
        model  = Oferta
        fields = ['producto', 'tipo_descuento', 'valor_descuento',
                  'descripcion', 'fecha_inicio', 'fecha_fin', 'limite_cantidad', 'activo']
        labels = {
            'producto':        'Seleccionar Producto',
            'tipo_descuento':  'Tipo de Descuento',
            'valor_descuento': 'Valor del Descuento',
            'descripcion':     'Descripción/Motivo',
            'fecha_inicio':    'Fecha y Hora de Inicio',
            'fecha_fin':       'Fecha y Hora de Fin',
            'limite_cantidad': 'Límite de cantidad en oferta (opcional)',
            'activo':          'Activar descuento de inmediato',
        }
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-xs focus:outline-none focus:border-[#2355a0] focus:bg-white transition-all text-gray-800'
            }),
            'tipo_descuento': forms.Select(attrs={
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-xs focus:outline-none focus:border-[#2355a0] focus:bg-white transition-all text-gray-800'
            }),
            'valor_descuento': forms.NumberInput(attrs={
                'step': '0.50',
                'min': '0',
                'placeholder': 'Ej: 15.00 (Bs. o %)',
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-xs focus:outline-none focus:border-[#2355a0] focus:bg-white transition-all text-gray-800 placeholder-gray-400'
            }),
            'descripcion': forms.TextInput(attrs={
                'placeholder': 'Ej: Promo Especial de Almuerzo',
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-xs focus:outline-none focus:border-[#2355a0] focus:bg-white transition-all text-gray-800 placeholder-gray-400'
            }),
            'fecha_inicio': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-xs focus:outline-none focus:border-[#2355a0] focus:bg-white transition-all text-gray-800'
            }),
            'fecha_fin': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-xs focus:outline-none focus:border-[#2355a0] focus:bg-white transition-all text-gray-800'
            }),
            'limite_cantidad': forms.NumberInput(attrs={
                'min': '1',
                'placeholder': 'Ej: 10 (Dejar vacío para todo el stock)',
                'class': 'w-full bg-gray-50 border border-gray-200 rounded-xl p-3.5 text-xs focus:outline-none focus:border-[#2355a0] focus:bg-white transition-all text-gray-800 placeholder-gray-400'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-[#2355a0] focus:ring-[#2355a0] h-4 w-4 transition-all'
            }),
        }