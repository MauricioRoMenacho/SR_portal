from django import forms
from .models import Salon, UtilEscolar, EntregaUtil


class SalonForm(forms.ModelForm):
    class Meta:
        model = Salon
        fields = ['nombre', 'codigo', 'profesora', 'grado', 'turno']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Salón 1A',
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: 1A',
                'maxlength': '10',
            }),
            'profesora': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: María López',
            }),
            'grado': forms.Select(attrs={
                'class': 'form-select',
            }),
            'turno': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'nombre': 'Nombre del Salón',
            'codigo': 'Código',
            'profesora': 'Nombre de la Profesora',
            'grado': 'Grado',
            'turno': 'Turno',
        }
        error_messages = {
            'nombre': {
                'required': 'Este campo es obligatorio.',
                'unique': 'Ya existe un salón con ese nombre.',
            },
            'codigo': {
                'required': 'Este campo es obligatorio.',
                'unique': 'Ya existe un salón con ese código.',
            },
            'profesora': {
                'required': 'Este campo es obligatorio.',
            },
        }


class UtilEscolarForm(forms.ModelForm):
    """
    Formulario para agregar útiles escolares a la lista del salón
    """
    
    class Meta:
        model = UtilEscolar
        fields = ['nombre', 'cantidad', 'descripcion']
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Cuaderno cuadriculado',
                'required': 'required'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 2',
                'min': '1',
                'value': '1',
                'required': 'required'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Tamaño A4, 100 hojas',
                'rows': 3
            })
        }
        
        labels = {
            'nombre': 'Nombre del útil',
            'cantidad': 'Cantidad',
            'descripcion': 'Descripción (opcional)'
        }
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre or nombre.strip() == '':
            raise forms.ValidationError("El nombre no puede estar vacío")
        return nombre.strip()
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad < 1:
            raise forms.ValidationError("La cantidad debe ser al menos 1")
        return cantidad


class EntregaUtilForm(forms.ModelForm):
    """
    Formulario para marcar entregas individuales
    """
    
    class Meta:
        model = EntregaUtil
        fields = ['entregado', 'observaciones']
        
        widgets = {
            'entregado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Observaciones sobre esta entrega...',
                'rows': 2
            })
        }
        
        labels = {
            'entregado': 'Entregado',
            'observaciones': 'Observaciones'
        }