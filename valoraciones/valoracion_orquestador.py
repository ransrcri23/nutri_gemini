import logging


logger = logging.getLogger(__name__)


class OrquestadorValoracion:
    def __init__(self):
        self.macronutrientes_calculator = MacronutrientesCalculator()
        self.plan_comidas_generator = PlanComidasGenerator()
        self.tabla_equivalencias_generator = TablaEquivalenciasGenerator()

    def actualizar_valoracion_completa(self, valoracion):
        try:
            # Calcular macronutrientes
            macros = self.macronutrientes_calculator.calcular(valoracion)
            self._actualizar_valoracion_con_macros(valoracion, macros)

            # Generar plan de comidas
            try:
                plan_comidas = self.plan_comidas_generator.generar(valoracion)
                valoracion.plan_comidas = plan_comidas
                valoracion.save()
                logger.info(f"Plan de comidas generado para valoración ID {valoracion.id}")
            except Exception as e:
                logger.warning(f"Error generando plan de comidas para valoración ID {valoracion.id}: {str(e)}")

            # Generar tabla de equivalencias
            try:
                tabla_equivalencias = self.tabla_equivalencias_generator.generar(valoracion)
                valoracion.tabla_equivalencias = tabla_equivalencias
                valoracion.save()
                logger.info(f"Tabla de equivalencias generada para valoración ID {valoracion.id}")
            except Exception as e:
                logger.warning(f"Error generando tabla de equivalencias para valoración ID {valoracion.id}: {str(e)}")

            logger.info(f"Valoración ID {valoracion.id} actualizada con macronutrientes")
            return valoracion
            
        except Exception as e:
            logger.error(f"Error actualizando valoración con macros: {str(e)}")
            raise

    def _actualizar_valoracion_con_macros(self, valoracion, macros):
        valoracion.carbohidratos_g = macros['carbohidratos_g']
        valoracion.proteinas_g = macros['proteinas_g']
        valoracion.grasas_g = macros['grasas_g']
        valoracion.calorias_totales = macros['calorias_totales']
        valoracion.recomendaciones = macros['recomendaciones']
        valoracion.save()


class MacronutrientesCalculator:
    def __init__(self):
        # Importar aquí para evitar importación circular
        from .services import NutricionCalculatorService
        self.service = NutricionCalculatorService()
    
    def calcular(self, valoracion):
        return self.service.calcular_macronutrientes(valoracion)


class PlanComidasGenerator:
    def __init__(self):
        # Importar aquí para evitar importación circular
        from .services import NutricionCalculatorService
        self.service = NutricionCalculatorService()
    
    def generar(self, valoracion):
        return self.service.calcular_plan_comidas(valoracion)


class TablaEquivalenciasGenerator:
    def __init__(self):
        # Importar aquí para evitar importación circular
        from .services import NutricionCalculatorService
        self.service = NutricionCalculatorService()
    
    def generar(self, valoracion):
        return self.service.calcular_tabla_equivalencias(valoracion)
