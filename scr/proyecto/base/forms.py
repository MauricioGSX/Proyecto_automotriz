from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['marca', 'modelo', 'placa']


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label='Nombre', max_length=30, required=True, help_text='Requerido. Ponga su primer nombre')
    last_name = forms.CharField(label='Apellido', max_length=30, required=True, help_text='Requerido. Ingrese su apellido.')
    email = forms.EmailField(label='Correo electrónico', max_length=254, required=True, help_text='Requerido. Introduzca una dirección de correo electrónico válida.')

    class Meta:
        model = User
        fields = ( 'first_name', 'last_name', 'email','username', 'password1', 'password2')

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['marca', 'modelo', 'placa'] 
    
    def clean_placa(self):
        placa = self.cleaned_data['placa']
        if Vehiculo.objects.filter(placa=placa).exists():
            raise forms.ValidationError("Ya existe un vehículo con esta patente.")
        if placa:
            return placa.upper()
        return placa

    def clean(self):
        cleaned_data = super().clean()
        marca = cleaned_data.get('marca')
        modelo = cleaned_data.get('modelo')
        
        if marca:
            cleaned_data['marca'] = marca.capitalize()
        
        if modelo:
            cleaned_data['modelo'] = modelo.capitalize()
        
        return cleaned_data
    
class CitaForm(forms.ModelForm):
    def __init__(self,user,*args,**kwargs):
        super(CitaForm,self).__init__(*args, **kwargs)
        self.fields['vehiculo'].queryset = Vehiculo.objects.filter(cliente=user)

    class Meta:
        model = Cita
        fields = ['vehiculo', 'fecha' , 'horario' , 'mecanico' , 'sucursal']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

class TrabajoForm(forms.ModelForm):
    class Meta:
        model = Trabajo
        fields = ['descripcion', 'estado']

class ChecklistForm(forms.ModelForm):
    class Meta:
        model = Checklist
        exclude = ('id', 'cita')  
        widgets = {
            'cita': forms.HiddenInput(), 
        }

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['numero_telefono', 'direccion', 'fecha_nacimiento']


class CustomPasswordChangeForm(PasswordChangeForm):
    repeat_new_password = forms.CharField(
        label="Repetir Nueva Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        repeat_new_password = cleaned_data.get('repeat_new_password')

        if new_password1 and repeat_new_password and new_password1 != repeat_new_password:
            raise ValidationError("Las contraseñas no coinciden.")

        return cleaned_data
    
class MecanicoForm(forms.ModelForm):
    class Meta:
        model = Mecanico
        fields = ['nombre']