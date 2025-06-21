from django import forms
from .models import PacienteNuevoB

class PacienteForm(forms.ModelForm):
    class Meta:
        model = PacienteNuevoB
        fields = ['nombre',
                  'apellidos', 
                  'fecha_nacimiento', 
                  'estatura', 
                  'peso',  
                  'ocupacion', 
                  'deportes', 
                  'horas_semana', 
                  'alergias', 
                  'condiciones_especiales', 
                  'objetivos']
