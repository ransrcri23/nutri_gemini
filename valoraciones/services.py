import google.generativeai as genai
import json
import logging
from django.conf import settings
from typing import Dict, Optional
from .models import Valoracion
from pacientes.models import Paciente

logger = logging.getLogger(__name__)

# Configurar Gemini
from django.conf import settings
import os

# Usar variable de entorno o fallback a la key original
API_KEY = os.environ.get('GOOGLE_API_KEY', 'AIzaSyDMkUp5NkWAoo9dLjJ7E3ozaRwVvIXoY9Q')
genai.configure(api_key=API_KEY)


class NutricionCalculatorService:
    """Servicio para calcular macronutrientes usando Gemini AI"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def calcular_plan_comidas(self, valoracion: Valoracion) -> str:
        """
        Genera un plan de comidas diarias con horarios y macronutrientes para un paciente específico.
        
        Args:
            valoracion: Instancia de Valoración con macronutrientes ya calculados
            
        Returns:
            String con el plan de comidas en formato HTML
            
        Raises:
            Exception: Si hay error en la generación o la API de Gemini
        """
        try:
            # Validar que la valoración tenga macronutrientes
            if not valoracion.tiene_macronutrientes:
                raise ValueError("La valoración debe tener macronutrientes calculados")
            
            # Construir el prompt para el plan de comidas
            prompt = self._construir_prompt_plan_comidas(valoracion)
            
            # Enviar prompt a Gemini
            response = self.model.generate_content(prompt)
            
            # Limpiar la respuesta HTML
            html_plan = self._limpiar_html_respuesta(response.text)
            
            logger.info(f"Plan de comidas generado exitosamente para valoración ID: {valoracion.id}")
            return html_plan
            
        except Exception as e:
            logger.error(f"Error generando plan de comidas: {str(e)}")
            raise Exception(f"Error en la generación del plan de comidas: {str(e)}")
    
    def calcular_tabla_equivalencias(self, valoracion: Valoracion) -> str:
        """
        Genera una tabla de equivalencias funcionales de alimentos para un paciente específico.
        
        Args:
            valoracion: Instancia de Valoración con macronutrientes ya calculados
            
        Returns:
            String con la tabla de equivalencias en formato HTML
            
        Raises:
            Exception: Si hay error en la generación o la API de Gemini
        """
        try:
            # Validar que la valoración tenga macronutrientes
            if not valoracion.tiene_macronutrientes:
                raise ValueError("La valoración debe tener macronutrientes calculados")
            
            # Construir el prompt para la tabla de equivalencias
            prompt = self._construir_prompt_tabla_equivalencias(valoracion)
            
            # Enviar prompt a Gemini
            response = self.model.generate_content(prompt)
            
            # Limpiar la respuesta HTML
            html_tabla = self._limpiar_html_respuesta(response.text)
            
            logger.info(f"Tabla de equivalencias generada exitosamente para valoración ID: {valoracion.id}")
            return html_tabla
            
        except Exception as e:
            logger.error(f"Error generando tabla de equivalencias: {str(e)}")
            raise Exception(f"Error en la generación de tabla de equivalencias: {str(e)}")
    
    def calcular_macronutrientes(self, valoracion: Valoracion) -> Dict[str, any]:
        """
        Calcula los macronutrientes para una valoración específica
        usando los datos del paciente y las mediciones físicas.
        
        Args:
            valoracion: Instancia de Valoración con mediciones físicas
            
        Returns:
            Dict con los macronutrientes calculados o None si hay error
            
        Raises:
            Exception: Si hay error en el cálculo o la API de Gemini
        """
        try:
            # Validar que la valoración tenga los datos necesarios
            if not valoracion.paciente:
                raise ValueError("La valoración debe estar asociada a un paciente")
            
            # Construir el prompt para Gemini
            prompt = self._construir_prompt(valoracion)
            
            # Enviar prompt a Gemini
            response = self.model.generate_content(prompt)
            
            # Parsear la respuesta
            resultado = self._parsear_respuesta(response.text)
            
            logger.info(f"Macronutrientes calculados exitosamente para valoración ID: {valoracion.id}")
            return resultado
            
        except Exception as e:
            logger.error(f"Error calculando macronutrientes: {str(e)}")
            raise Exception(f"Error en el cálculo nutricional: {str(e)}")
    
    def _construir_prompt_tabla_equivalencias(self, valoracion: Valoracion) -> str:
        """Construye el prompt específico para generar tabla de equivalencias"""
        paciente = valoracion.paciente
        
        prompt = f"""
Como experto en nutrición, necesito que generes una tabla de equivalencias funcionales de alimentos específicamente para este paciente:

**INFORMACIÓN DEL PACIENTE:**
- Nombre: {paciente.nombre} {paciente.apellidos}
- Edad: {paciente.edad} años
- Estatura: {paciente.estatura} metros
- Objetivos: {paciente.objetivos}
- Alergias: {paciente.alergias or 'Ninguna'}

**MACRONUTRIENTES DIARIOS DEL PACIENTE:**
- Carbohidratos: {valoracion.carbohidratos_g}g diarios
- Proteínas: {valoracion.proteinas_g}g diarios
- Grasas: {valoracion.grasas_g}g diarios
- Calorías totales: {valoracion.calorias_totales} kcal diarias

**INSTRUCCIONES:**
Genera una tabla de equivalencias funcionales organizada por categorías. Para cada alimento, indica la cantidad que proporciona una unidad estándar de ese macronutriente:

- Para CARBOHIDRATOS: cantidad que aporta 15g de carbohidratos
- Para PROTEÍNAS: cantidad que aporta 7g de proteína  
- Para GRASAS: cantidad que aporta 5g de grasa

Incluye al menos 10 alimentos por categoría, usando medidas prácticas y caseras (tazas, cucharadas, unidades, gramos). Considera las alergias del paciente.

**FORMATO DE RESPUESTA:**
Responde ÚNICAMENTE con HTML limpio usando la siguiente estructura:

<div class="tabla-equivalencias">
    <h4><i class="fas fa-bread-slice text-primary"></i> Carbohidratos (15g por porción)</h4>
    <div class="row">
        <div class="col-md-6">
            <ul class="list-unstyled">
                <li>• Alimento - cantidad</li>
                ...
            </ul>
        </div>
        <div class="col-md-6">
            <ul class="list-unstyled">
                <li>• Alimento - cantidad</li>
                ...
            </ul>
        </div>
    </div>
    
    <h4 class="mt-4"><i class="fas fa-drumstick-bite text-success"></i> Proteínas (7g por porción)</h4>
    <div class="row">
        <div class="col-md-6">
            <ul class="list-unstyled">
                <li>• Alimento - cantidad</li>
                ...
            </ul>
        </div>
        <div class="col-md-6">
            <ul class="list-unstyled">
                <li>• Alimento - cantidad</li>
                ...
            </ul>
        </div>
    </div>
    
    <h4 class="mt-4"><i class="fas fa-seedling text-warning"></i> Grasas (5g por porción)</h4>
    <div class="row">
        <div class="col-md-6">
            <ul class="list-unstyled">
                <li>• Alimento - cantidad</li>
                ...
            </ul>
        </div>
        <div class="col-md-6">
            <ul class="list-unstyled">
                <li>• Alimento - cantidad</li>
                ...
            </ul>
        </div>
    </div>
</div>

Responde ÚNICAMENTE con el HTML, sin explicaciones adicionales.
"""
        
        return prompt
    
    def _construir_prompt_plan_comidas(self, valoracion: Valoracion) -> str:
        """Construye el prompt específico para generar plan de comidas diarias"""
        paciente = valoracion.paciente
        
        prompt = f"""
Como experto en nutrición, necesito que generes un plan de comidas diarias con horarios y distribución de macronutrientes para este paciente:

**INFORMACIÓN DEL PACIENTE:**
- Nombre: {paciente.nombre} {paciente.apellidos}
- Edad: {paciente.edad} años
- Estatura: {paciente.estatura} metros
- Ocupación: {paciente.ocupacion}
- Deportes: {paciente.deportes}
- Horas de ejercicio/semana: {paciente.horas_semana}
- Objetivos: {paciente.objetivos}
- Alergias: {paciente.alergias or 'Ninguna'}

**MACRONUTRIENTES DIARIOS DEL PACIENTE:**
- Carbohidratos: {valoracion.carbohidratos_g}g diarios
- Proteínas: {valoracion.proteinas_g}g diarios
- Grasas: {valoracion.grasas_g}g diarios
- Calorías totales: {valoracion.calorias_totales} kcal diarias

**INSTRUCCIONES:**
Genera un plan de comidas diarias que incluya:
1. 5-6 tiempos de comida distribuidos a lo largo del día
2. Horarios apropiados para cada comida
3. Distribución específica de macronutrientes para cada tiempo de comida
4. Considera la ocupación y horarios de ejercicio del paciente
5. Asegúrate de que la suma de todos los macronutrientes sea igual a los totales diarios

**FORMATO DE RESPUESTA:**
Responde ÚNICAMENTE con HTML limpio usando la siguiente estructura:

<div class="plan-comidas">
    <div class="timeline">
        <div class="time-item">
            <div class="time-hour">
                <i class="fas fa-clock text-primary"></i>
                <span class="fw-bold">7:00 AM</span>
            </div>
            <div class="time-content">
                <h6 class="mb-2"><i class="fas fa-coffee text-warning"></i> Desayuno</h6>
                <div class="macros-distribution">
                    <small class="badge bg-primary me-1">XXg carbohidratos</small>
                    <small class="badge bg-success me-1">XXg proteínas</small>
                    <small class="badge bg-warning text-dark">XXg grasas</small>
                </div>
            </div>
        </div>
        
        <div class="time-item">
            <div class="time-hour">
                <i class="fas fa-clock text-primary"></i>
                <span class="fw-bold">10:00 AM</span>
            </div>
            <div class="time-content">
                <h6 class="mb-2"><i class="fas fa-apple-alt text-success"></i> Merienda Matutina</h6>
                <div class="macros-distribution">
                    <small class="badge bg-primary me-1">XXg carbohidratos</small>
                    <small class="badge bg-success me-1">XXg proteínas</small>
                </div>
            </div>
        </div>
        
        <!-- Continúa con más comidas siguiendo el mismo patrón -->
    </div>
</div>

Responde ÚNICAMENTE con el HTML, sin explicaciones adicionales. Asegúrate de incluir todos los tiempos de comida necesarios y que los macronutrientes sumen correctamente.
"""
        
        return prompt
    
    def _construir_prompt(self, valoracion: Valoracion) -> str:
        """Construye el prompt detallado para enviar a Gemini"""
        paciente = valoracion.paciente
        
        prompt = f"""
Como experto en nutrición, necesito que calcules los macronutrientes diarios recomendados para el siguiente paciente:

**INFORMACIÓN DEL PACIENTE:**
- Nombre: {paciente.nombre} {paciente.apellidos}
- Edad: {paciente.edad} años
- Estatura: {paciente.estatura} metros
- Ocupación: {paciente.ocupacion}
- Deportes que practica: {paciente.deportes}
- Horas de ejercicio por semana: {paciente.horas_semana}
- Alergias: {paciente.alergias or 'Ninguna'}
- Condiciones especiales: {paciente.condiciones_especiales or 'Ninguna'}
- Objetivos: {paciente.objetivos}

**MEDICIONES CORPORALES ACTUALES:**
- Peso total: {valoracion.peso_kg} kg
- Grasa corporal: {valoracion.kg_grasa} kg
- Proteína corporal: {valoracion.kg_proteinas} kg
- Minerales: {valoracion.kg_minerales} kg
- Agua corporal: {valoracion.litros_agua} litros

**INSTRUCCIONES:**
1. Calcula los macronutrientes diarios recomendados (carbohidratos, proteínas, grasas)
2. Determina las calorías totales diarias necesarias
3. Proporciona recomendaciones nutricionales específicas considerando:
   - Composición corporal actual
   - Nivel de actividad física
   - Objetivos del paciente
   - Alergias y condiciones especiales

   
**FORMATO DE RESPUESTA REQUERIDO (JSON):**
{{
    "carbohidratos_g": [número en gramos],
    "proteinas_g": [número en gramos],
    "grasas_g": [número en gramos],
    "calorias_totales": [número entero de calorías],
    "recomendaciones": "[texto detallado con recomendaciones específicas.]"
}}

Por favor responde ÚNICAMENTE con el JSON válido, sin texto adicional.
"""
        
        return prompt
    
    def _limpiar_html_respuesta(self, respuesta: str) -> str:
        """Limpia la respuesta HTML de Gemini removiendo etiquetas de código"""
        respuesta_limpia = respuesta.strip()
        
        # Remover etiquetas de código markdown si existen
        if '```html' in respuesta_limpia:
            inicio = respuesta_limpia.find('```html') + 7
            fin = respuesta_limpia.find('```', inicio)
            if fin != -1:
                respuesta_limpia = respuesta_limpia[inicio:fin].strip()
        elif '```' in respuesta_limpia:
            inicio = respuesta_limpia.find('```') + 3
            fin = respuesta_limpia.find('```', inicio)
            if fin != -1:
                respuesta_limpia = respuesta_limpia[inicio:fin].strip()
        
        return respuesta_limpia
    
    def _parsear_respuesta(self, respuesta: str) -> Dict[str, any]:
        """Parsea la respuesta JSON de Gemini"""
        try:
            # Limpiar la respuesta removiendo posibles caracteres extra
            respuesta_limpia = respuesta.strip()
            
            # Si la respuesta está envuelta en ```json, extraer solo el JSON
            if '```json' in respuesta_limpia:
                inicio = respuesta_limpia.find('```json') + 7
                fin = respuesta_limpia.find('```', inicio)
                respuesta_limpia = respuesta_limpia[inicio:fin].strip()
            elif '```' in respuesta_limpia:
                inicio = respuesta_limpia.find('```') + 3
                fin = respuesta_limpia.find('```', inicio)
                respuesta_limpia = respuesta_limpia[inicio:fin].strip()
            
            # Parsear JSON
            resultado = json.loads(respuesta_limpia)
            
            # Validar campos requeridos
            campos_requeridos = ['carbohidratos_g', 'proteinas_g', 'grasas_g', 'calorias_totales', 'recomendaciones']
            for campo in campos_requeridos:
                if campo not in resultado:
                    raise ValueError(f"Campo requerido '{campo}' no encontrado en la respuesta")
            
            # Validar tipos de datos
            for campo in ['carbohidratos_g', 'proteinas_g', 'grasas_g']:
                if not isinstance(resultado[campo], (int, float)):
                    raise ValueError(f"El campo '{campo}' debe ser numérico")
            
            if not isinstance(resultado['calorias_totales'], int):
                # Intentar convertir a entero
                resultado['calorias_totales'] = int(float(resultado['calorias_totales']))
            
            if not isinstance(resultado['recomendaciones'], str):
                raise ValueError("El campo 'recomendaciones' debe ser texto")
            
            return resultado
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parseando JSON de Gemini: {str(e)}. Respuesta: {respuesta}")
        except Exception as e:
            raise ValueError(f"Error procesando respuesta: {str(e)}")
    
    def actualizar_valoracion_con_macros(self, valoracion: Valoracion) -> Valoracion:
        """
        Calcula y actualiza los macronutrientes y tabla de equivalencias en una valoración.
        
        Args:
            valoracion: Instancia de Valoración a actualizar
            
        Returns:
            Valoración actualizada con macronutrientes y tabla de equivalencias
            
        Raises:
            Exception: Si hay error en el cálculo
        """
        try:
            # Calcular macronutrientes
            macros = self.calcular_macronutrientes(valoracion)
            
            # Actualizar valoración con macronutrientes
            valoracion.carbohidratos_g = macros['carbohidratos_g']
            valoracion.proteinas_g = macros['proteinas_g']
            valoracion.grasas_g = macros['grasas_g']
            valoracion.calorias_totales = macros['calorias_totales']
            valoracion.recomendaciones = macros['recomendaciones']
            
            # Guardar primero los macronutrientes
            valoracion.save()
            
            # Ahora generar el plan de comidas (necesita los macros ya guardados)
            try:
                plan_comidas = self.calcular_plan_comidas(valoracion)
                valoracion.plan_comidas = plan_comidas
                valoracion.save()
                logger.info(f"Plan de comidas generado para valoración ID {valoracion.id}")
            except Exception as e:
                # Si falla el plan de comidas, log el error pero no falle todo el proceso
                logger.warning(f"Error generando plan de comidas para valoración ID {valoracion.id}: {str(e)}")
                # La valoración queda con macronutrientes pero sin plan de comidas
            
            # Ahora generar la tabla de equivalencias (necesita los macros ya guardados)
            try:
                tabla_equivalencias = self.calcular_tabla_equivalencias(valoracion)
                valoracion.tabla_equivalencias = tabla_equivalencias
                valoracion.save()
                logger.info(f"Tabla de equivalencias generada para valoración ID {valoracion.id}")
            except Exception as e:
                # Si falla la tabla de equivalencias, log el error pero no falle todo el proceso
                logger.warning(f"Error generando tabla de equivalencias para valoración ID {valoracion.id}: {str(e)}")
                # La valoración queda con macronutrientes pero sin tabla de equivalencias
            
            logger.info(f"Valoración ID {valoracion.id} actualizada con macronutrientes")
            return valoracion
            
        except Exception as e:
            logger.error(f"Error actualizando valoración con macros: {str(e)}")
            raise
    
    def regenerar_tabla_equivalencias(self, valoracion: Valoracion) -> Valoracion:
        """
        Regenera únicamente la tabla de equivalencias para una valoración que ya tiene macronutrientes.
        
        Args:
            valoracion: Instancia de Valoración con macronutrientes ya calculados
            
        Returns:
            Valoración actualizada con nueva tabla de equivalencias
            
        Raises:
            Exception: Si hay error en la regeneración
        """
        try:
            if not valoracion.tiene_macronutrientes:
                raise ValueError("La valoración debe tener macronutrientes calculados")
            
            # Generar nueva tabla de equivalencias
            tabla_equivalencias = self.calcular_tabla_equivalencias(valoracion)
            valoracion.tabla_equivalencias = tabla_equivalencias
            valoracion.save()
            
            logger.info(f"Tabla de equivalencias regenerada para valoración ID {valoracion.id}")
            return valoracion
            
        except Exception as e:
            logger.error(f"Error regenerando tabla de equivalencias: {str(e)}")
            raise
    
    def regenerar_plan_comidas(self, valoracion: Valoracion) -> Valoracion:
        """
        Regenera únicamente el plan de comidas para una valoración que ya tiene macronutrientes.
        
        Args:
            valoracion: Instancia de Valoración con macronutrientes ya calculados
            
        Returns:
            Valoración actualizada con nuevo plan de comidas
            
        Raises:
            Exception: Si hay error en la regeneración
        """
        try:
            if not valoracion.tiene_macronutrientes:
                raise ValueError("La valoración debe tener macronutrientes calculados")
            
            # Generar nuevo plan de comidas
            plan_comidas = self.calcular_plan_comidas(valoracion)
            valoracion.plan_comidas = plan_comidas
            valoracion.save()
            
            logger.info(f"Plan de comidas regenerado para valoración ID {valoracion.id}")
            return valoracion
            
        except Exception as e:
            logger.error(f"Error regenerando plan de comidas: {str(e)}")
            raise


# Instancia global del servicio
nutricion_calculator = NutricionCalculatorService()

