from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from .models import Valoracion
from .services import nutricion_calculator
from pacientes.models import Paciente
from usuarios.models import TipoUsuario
import json


def es_nutricionista_o_admin(user):
    """Verifica si el usuario es nutricionista o administrador"""
    if not user.is_authenticated:
        return False
    return user.tipo_usuario in [TipoUsuario.NUTRICIONISTA, TipoUsuario.ADMINISTRADOR]


def lista_valoraciones(request):
    """Lista todas las valoraciones de pacientes ACTIVOS solamente"""
    valoraciones = Valoracion.objects.select_related('paciente').filter(paciente__activo=True)
    return render(request, 'valoraciones/lista.html', {
        'valoraciones': valoraciones
    })


def detalle_valoracion(request, valoracion_id):
    """Muestra el detalle de una valoración"""
    valoracion = get_object_or_404(Valoracion, id=valoracion_id)
    return render(request, 'valoraciones/detalle.html', {
        'valoracion': valoracion
    })


def crear_valoracion(request, paciente_id):
    """Crear nueva valoración para un paciente"""
    paciente = get_object_or_404(Paciente, id=paciente_id, activo=True)
    
    if request.method == 'POST':
        try:
            # Extraer datos del formulario
            peso_kg = float(request.POST.get('peso_kg'))
            kg_grasa = float(request.POST.get('kg_grasa'))
            kg_proteinas = float(request.POST.get('kg_proteinas'))
            kg_minerales = float(request.POST.get('kg_minerales'))
            litros_agua = float(request.POST.get('litros_agua'))
            notas = request.POST.get('notas', '')
            
            # Crear valoración (sin macronutrientes aún)
            valoracion = Valoracion(
                paciente=paciente,
                peso_kg=peso_kg,
                kg_grasa=kg_grasa,
                kg_proteinas=kg_proteinas,
                kg_minerales=kg_minerales,
                litros_agua=litros_agua,
                notas=notas
            )
            
            # Validar antes de guardar (esto validará que los componentes sumen el peso total)
            valoracion.clean()
            valoracion.save()
            
            # Intentar calcular macronutrientes con Gemini
            try:
                valoracion = nutricion_calculator.actualizar_valoracion_con_macros(valoracion)
                messages.success(request, 'Valoración creada exitosamente y macronutrientes calculados.')
            except Exception as e:
                # Si falla Gemini, borrar la valoración y mostrar error
                valoracion.delete()
                messages.error(request, f'Error calculando macronutrientes: {str(e)}. La valoración no fue guardada.')
                return render(request, 'valoraciones/crear.html', {
                    'paciente': paciente,
                    'error': str(e)
                })
            
            return redirect('detalle_valoracion', valoracion_id=valoracion.id)
            
        except ValidationError as e:
            messages.error(request, f'Error de validación: {str(e)}')
        except ValueError as e:
            messages.error(request, f'Error en los datos ingresados: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
    
    return render(request, 'valoraciones/crear.html', {
        'paciente': paciente
    })


@require_http_methods(["POST"])
def recalcular_macronutrientes(request, valoracion_id):
    """Recalcula los macronutrientes de una valoración existente"""
    try:
        valoracion = get_object_or_404(Valoracion, id=valoracion_id)
        
        # Recalcular macronutrientes
        valoracion = nutricion_calculator.actualizar_valoracion_con_macros(valoracion)
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True,
                'message': 'Macronutrientes y tabla de equivalencias recalculados exitosamente',
                'carbohidratos_g': valoracion.carbohidratos_g,
                'proteinas_g': valoracion.proteinas_g,
                'grasas_g': valoracion.grasas_g,
                'calorias_totales': valoracion.calorias_totales,
                'recomendaciones': valoracion.recomendaciones,
                'tabla_equivalencias': valoracion.tabla_equivalencias
            })
        else:
            messages.success(request, 'Macronutrientes y tabla de equivalencias recalculados exitosamente.')
            return redirect('detalle_valoracion', valoracion_id=valoracion.id)
    
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        else:
            messages.error(request, f'Error recalculando macronutrientes: {str(e)}')
            return redirect('detalle_valoracion', valoracion_id=valoracion_id)


@require_http_methods(["POST"])
@login_required
@user_passes_test(es_nutricionista_o_admin)
def regenerar_tabla_equivalencias(request, valoracion_id):
    """Regenera únicamente la tabla de equivalencias de una valoración existente"""
    try:
        valoracion = get_object_or_404(Valoracion, id=valoracion_id)
        
        # Regenerar tabla de equivalencias
        valoracion = nutricion_calculator.regenerar_tabla_equivalencias(valoracion)
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True,
                'message': 'Tabla de equivalencias regenerada exitosamente',
                'tabla_equivalencias': valoracion.tabla_equivalencias
            })
        else:
            messages.success(request, 'Tabla de equivalencias regenerada exitosamente.')
            return redirect('detalle_valoracion', valoracion_id=valoracion.id)
    
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        else:
            messages.error(request, f'Error regenerando tabla de equivalencias: {str(e)}')
            return redirect('detalle_valoracion', valoracion_id=valoracion_id)


@require_http_methods(["POST"])
@login_required
@user_passes_test(es_nutricionista_o_admin)
def regenerar_plan_comidas(request, valoracion_id):
    """Regenera únicamente el plan de comidas de una valoración existente"""
    try:
        valoracion = get_object_or_404(Valoracion, id=valoracion_id)
        
        # Regenerar plan de comidas
        valoracion = nutricion_calculator.regenerar_plan_comidas(valoracion)
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True,
                'message': 'Plan de comidas regenerado exitosamente',
                'plan_comidas': valoracion.plan_comidas
            })
        else:
            messages.success(request, 'Plan de comidas regenerado exitosamente.')
            return redirect('detalle_valoracion', valoracion_id=valoracion.id)
    
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        else:
            messages.error(request, f'Error regenerando plan de comidas: {str(e)}')
            return redirect('detalle_valoracion', valoracion_id=valoracion_id)


def valoraciones_paciente(request, paciente_id):
    """Lista todas las valoraciones de un paciente específico"""
    paciente = get_object_or_404(Paciente, id=paciente_id, activo=True)
    valoraciones = paciente.valoraciones.all()
    
    return render(request, 'valoraciones/paciente.html', {
        'paciente': paciente,
        'valoraciones': valoraciones
    })


# === FUNCIONES PARA NUTRICIONISTAS Y ADMINISTRADORES ===

@login_required
@user_passes_test(es_nutricionista_o_admin)
def lista_valoraciones_todas(request):
    """Lista TODAS las valoraciones (incluyendo de pacientes inactivos) para nutricionistas y admins"""
    # Solo mostrar valoraciones de pacientes activos por defecto
    incluir_inactivos = request.GET.get('incluir_inactivos') == 'true'
    
    if incluir_inactivos:
        valoraciones = Valoracion.objects.select_related('paciente').all()
    else:
        valoraciones = Valoracion.objects.select_related('paciente').filter(paciente__activo=True)
    
    return render(request, 'valoraciones/lista_todas.html', {
        'valoraciones': valoraciones,
        'incluir_inactivos': incluir_inactivos
    })


@login_required
@user_passes_test(es_nutricionista_o_admin)
def editar_valoracion(request, valoracion_id):
    """Permite a nutricionistas y admins editar valoraciones"""
    valoracion = get_object_or_404(Valoracion, id=valoracion_id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos de la valoración
            valoracion.peso_kg = float(request.POST.get('peso_kg'))
            valoracion.kg_grasa = float(request.POST.get('kg_grasa'))
            valoracion.kg_proteinas = float(request.POST.get('kg_proteinas'))
            valoracion.kg_minerales = float(request.POST.get('kg_minerales'))
            valoracion.litros_agua = float(request.POST.get('litros_agua'))
            valoracion.notas = request.POST.get('notas', '')
            
            # Actualizar macronutrientes si se proporcionan
            if request.POST.get('carbohidratos_g'):
                valoracion.carbohidratos_g = float(request.POST.get('carbohidratos_g'))
            if request.POST.get('proteinas_g'):
                valoracion.proteinas_g = float(request.POST.get('proteinas_g'))
            if request.POST.get('grasas_g'):
                valoracion.grasas_g = float(request.POST.get('grasas_g'))
            if request.POST.get('calorias_totales'):
                valoracion.calorias_totales = int(request.POST.get('calorias_totales'))
            if request.POST.get('recomendaciones'):
                valoracion.recomendaciones = request.POST.get('recomendaciones')
            if request.POST.get('plan_comidas'):
                valoracion.plan_comidas = request.POST.get('plan_comidas')
            if request.POST.get('tabla_equivalencias'):
                valoracion.tabla_equivalencias = request.POST.get('tabla_equivalencias')
            
            # Validar antes de guardar
            valoracion.clean()
            valoracion.save()
            
            messages.success(request, 'Valoración actualizada exitosamente.')
            return redirect('detalle_valoracion', valoracion_id=valoracion.id)
            
        except ValidationError as e:
            messages.error(request, f'Error de validación: {str(e)}')
        except ValueError as e:
            messages.error(request, f'Error en los datos ingresados: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
    
    return render(request, 'valoraciones/editar.html', {
        'valoracion': valoracion
    })


@login_required
@user_passes_test(es_nutricionista_o_admin)
def valoraciones_paciente_todas(request, paciente_id):
    """Lista TODAS las valoraciones de un paciente (incluso si está inactivo) para nutricionistas y admins"""
    paciente = get_object_or_404(Paciente, id=paciente_id)  # Sin filtro de activo
    valoraciones = paciente.valoraciones.all()
    
    return render(request, 'valoraciones/paciente_todas.html', {
        'paciente': paciente,
        'valoraciones': valoraciones
    })
