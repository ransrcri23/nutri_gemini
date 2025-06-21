from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Paciente(models.Model):
    # Información básica del paciente
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo_electronico = models.EmailField(max_length=254, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    estatura = models.FloatField(help_text="Estatura en metros (ej: 1.75)")
    
    # Información de estilo de vida
    ocupacion = models.CharField(max_length=100)
    deportes = models.CharField(max_length=200, help_text="Deportes que practica")
    horas_semana = models.CharField(max_length=50, help_text="Horas de ejercicio por semana")
    
    # Información médica
    alergias = models.TextField(blank=True, help_text="Alergias alimentarias o de otro tipo")
    condiciones_especiales = models.TextField(blank=True, help_text="Condiciones médicas especiales")
    objetivos = models.TextField(help_text="Objetivos nutricionales del paciente")
    
    # Campos de auditoría
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pacientes'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
    
    def __str__(self):
        return f"{self.nombre} {self.apellidos}"
    
    @property
    def edad(self):
        "Calcula la edad del paciente"
        today = timezone.now().date()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )



# Mantener el modelo anterior para migración gradual
class PacienteNuevoB(models.Model):
    """DEPRECATED: Usar el modelo Paciente en su lugar"""
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    estatura = models.FloatField()
    peso = models.FloatField()
    ocupacion = models.CharField(max_length=100, blank=True, null=True)
    deportes = models.CharField(max_length=100, blank=True, null=True)
    horas_semana = models.CharField(max_length=100, blank=True, null=True)
    alergias = models.CharField(max_length=100, blank=True, null=True)
    condiciones_especiales = models.TextField(blank=True, null=True)
    objetivos = models.TextField(blank=True, null=True)
    
    # Campos de macronutrientes descompuestos
    carbohidratos_g = models.FloatField(null=True, blank=True)
    proteinas_g = models.FloatField(null=True, blank=True)
    grasas_g = models.FloatField(null=True, blank=True)
    calorias_totales = models.IntegerField(null=True, blank=True)
    recomendaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"
