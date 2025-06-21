from django.db import models
from django.core.exceptions import ValidationError
from pacientes.models import Paciente


class Valoracion(models.Model):
    # Relación con el paciente
    paciente = models.ForeignKey(
        Paciente, 
        on_delete=models.CASCADE, 
        related_name='valoraciones'
    )
    
    # Mediciones físicas tomadas por el nutricionista
    peso_kg = models.FloatField(help_text="Peso total en kilogramos")
    kg_grasa = models.FloatField(help_text="Kilogramos de grasa corporal")
    kg_proteinas = models.FloatField(help_text="Kilogramos de proteína corporal")
    kg_minerales = models.FloatField(help_text="Kilogramos de minerales")
    litros_agua = models.FloatField(help_text="Litros de agua corporal")
    
    # Macronutrientes calculados por Gemini
    carbohidratos_g = models.FloatField(null=True, blank=True, help_text="Carbohidratos recomendados en gramos")
    proteinas_g = models.FloatField(null=True, blank=True, help_text="Proteínas recomendadas en gramos")
    grasas_g = models.FloatField(null=True, blank=True, help_text="Grasas recomendadas en gramos")
    calorias_totales = models.IntegerField(null=True, blank=True, help_text="Calorías totales recomendadas")
    recomendaciones = models.TextField(null=True, blank=True, help_text="Recomendaciones nutricionales específicas")
    plan_comidas = models.TextField(null=True, blank=True, help_text="Plan de comidas diarias con horarios y macronutrientes")
    tabla_equivalencias = models.TextField(null=True, blank=True, help_text="Tabla de equivalencias funcionales de alimentos")
    
    # Notas del nutricionista
    notas = models.TextField(blank=True, help_text="Observaciones adicionales del nutricionista")
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'valoraciones'
        verbose_name = 'Valoración'
        verbose_name_plural = 'Valoraciones'
        ordering = ['-fecha_creacion']  # Más recientes primero
    
    def clean(self):
        """Validación personalizada para asegurar que los componentes sumen el peso total"""
        super().clean()
        
        # Validar que la suma de componentes sea igual al peso total (con tolerancia)
        suma_componentes = self.kg_grasa + self.kg_proteinas + self.kg_minerales + self.litros_agua
        tolerancia = 0.5  # 500 gramos de tolerancia
        
        if abs(suma_componentes - self.peso_kg) > tolerancia:
            raise ValidationError(
                f"Los componentes corporales ({suma_componentes:.2f} kg) no suman el peso total ({self.peso_kg:.2f} kg). "
                f"Diferencia: {abs(suma_componentes - self.peso_kg):.2f} kg (tolerancia: {tolerancia} kg)"
            )
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Valoración de {self.paciente.nombre} {self.paciente.apellidos} - {self.fecha_creacion.strftime('%d/%m/%Y')}"
    
    @property
    def tiene_macronutrientes(self):
        """Verifica si la valoración ya tiene los macronutrientes calculados"""
        return all([
            self.carbohidratos_g is not None,
            self.proteinas_g is not None,
            self.grasas_g is not None,
            self.calorias_totales is not None
        ])
