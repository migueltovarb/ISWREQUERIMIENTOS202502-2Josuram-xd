from django import forms
from .models import vehiculo

class vehiculoForm(forms.ModelForm):
    class Meta:
        model = vehiculo
        fields = [
            'placa',
            'marca',
            'modelo',
            'color'
            ]
        
        labels = {
            'placa': 'Placa del Vehículo',
            'marca': 'Marca del Vehículo',
            'modelo': 'Modelo del Vehículo',
            'color': 'Color del Vehículo',
        }

        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-control'}),
        }