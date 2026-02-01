from django import forms
from .models import Salon


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