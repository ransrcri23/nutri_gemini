from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .models import Valoracion
from .services import nutricion_calculator
from pacientes.models import Paciente
from usuarios.models import TipoUsuario
import re
from html import unescape
import json
from bs4 import BeautifulSoup


def html_to_readable_text(html_content):
    """
    Convierte contenido HTML a texto legible para edición
    """
    if not html_content:
        return ""
    
    try:
        # Parsear el HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Encontrar elementos específicos del plan de comidas
        if soup.find(class_='plan-comidas'):
            return _convert_plan_comidas_to_text(soup)
        elif soup.find(class_='tabla-equivalencias'):
            return _convert_tabla_equivalencias_to_text(soup)
        else:
            # Si no es un formato conocido, extraer texto simple
            return soup.get_text(separator='\n', strip=True)
    except Exception:
        # Si falla el parsing, devolver el HTML original
        return html_content


def _convert_plan_comidas_to_text(soup):
    """
    Convierte el HTML del plan de comidas a texto estructurado
    """
    text_lines = []
    text_lines.append("=== PLAN DE COMIDAS DIARIAS ===")
    text_lines.append("")
    
    # Buscar todos los elementos de tiempo
    time_items = soup.find_all(class_='time-item')
    
    for item in time_items:
        # Extraer hora
        time_hour = item.find(class_='time-hour')
        if time_hour:
            hora = time_hour.find('span', class_='fw-bold')
            if hora:
                text_lines.append(f"⏰ {hora.get_text(strip=True)}")
        
        # Extraer contenido de la comida
        time_content = item.find(class_='time-content')
        if time_content:
            # Nombre de la comida
            titulo = time_content.find('h6')
            if titulo:
                nombre_comida = titulo.get_text(strip=True)
                text_lines.append(f"   {nombre_comida}")
            
            # Macronutrientes
            badges = time_content.find_all('small', class_='badge')
            if badges:
                macros = []
                for badge in badges:
                    texto = badge.get_text(strip=True)
                    macros.append(f"     • {texto}")
                text_lines.extend(macros)
        
        text_lines.append("")  # Línea en blanco entre comidas
    
    # Buscar resumen diario
    daily_summary = soup.find(class_='daily-summary')
    if daily_summary:
        text_lines.append("=== RESUMEN DIARIO ===")
        badges = daily_summary.find_all('small', class_='badge')
        for badge in badges:
            texto = badge.get_text(strip=True)
            text_lines.append(f"• {texto}")
    
    return "\n".join(text_lines)


def _convert_tabla_equivalencias_to_text(soup):
    """
    Convierte el HTML de la tabla de equivalencias a texto estructurado
    """
    text_lines = []
    text_lines.append("=== TABLA DE EQUIVALENCIAS ===")
    text_lines.append("")
    
    # Buscar secciones por h4
    sections = soup.find_all('h4')
    
    for section in sections:
        # Título de la sección
        titulo = section.get_text(strip=True)
        text_lines.append(f"📋 {titulo}")
        text_lines.append("")
        
        # Buscar la siguiente div row después del h4
        next_div = section.find_next_sibling('div', class_='row')
        if next_div:
            # Buscar todas las listas
            lists = next_div.find_all('ul')
            for ul in lists:
                items = ul.find_all('li')
                for li in items:
                    texto = li.get_text(strip=True)
                    if texto.startswith('•'):
                        text_lines.append(f"  {texto}")
                    else:
                        text_lines.append(f"  • {texto}")
        
        text_lines.append("")  # Línea en blanco entre secciones
    
    return "\n".join(text_lines)


def readable_text_to_html(text_content, content_type):
    """
    Convierte texto legible de vuelta a HTML estructurado
    """
    if not text_content or not text_content.strip():
        return ""
    
    lines = text_content.strip().split('\n')
    
    if content_type == 'plan_comidas':
        return _convert_text_to_plan_comidas_html(lines)
    elif content_type == 'tabla_equivalencias':
        return _convert_text_to_tabla_equivalencias_html(lines)
    else:
        # Si no es un formato conocido, crear HTML básico preservando el formato
        return _convert_text_to_basic_html(text_content)


def _convert_text_to_plan_comidas_html(lines):
    """
    Convierte texto del plan de comidas a HTML estructurado
    """
    html_parts = []
    html_parts.append('<div class="plan-comidas">')
    html_parts.append('    <div class="timeline">')
    
    current_time_item = None
    current_macros = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('==='):
            continue
            
        if line.startswith('⏰'):
            # Cerrar item anterior si existe
            if current_time_item:
                if current_macros:
                    html_parts.append('                <div class="macros-distribution">')
                    for macro in current_macros:
                        html_parts.append(f'                    <small class="badge bg-primary me-1">{macro}</small>')
                    html_parts.append('                </div>')
                html_parts.append('            </div>')
                html_parts.append('        </div>')
            
            # Iniciar nuevo item
            time = line.replace('⏰', '').strip()
            html_parts.append('        <div class="time-item">')
            html_parts.append('            <div class="time-hour">')
            html_parts.append('                <i class="fas fa-clock text-primary"></i>')
            html_parts.append(f'                <span class="fw-bold">{time}</span>')
            html_parts.append('            </div>')
            html_parts.append('            <div class="time-content">')
            current_time_item = True
            current_macros = []
            
        elif line.startswith('   ') and not line.startswith('     •'):
            # Título de comida
            meal_name = line.strip()
            icon = _get_meal_icon(meal_name)
            html_parts.append(f'                <h6 class="mb-2"><i class="{icon}"></i> {meal_name}</h6>')
            
        elif line.startswith('     •'):
            # Macronutriente
            macro = line.replace('     •', '').strip()
            current_macros.append(macro)
        
        elif line.startswith('•') and 'kcal' in line:
            # Resumen diario
            if current_time_item:
                if current_macros:
                    html_parts.append('                <div class="macros-distribution">')
                    for macro in current_macros:
                        html_parts.append(f'                    <small class="badge bg-primary me-1">{macro}</small>')
                    html_parts.append('                </div>')
                html_parts.append('            </div>')
                html_parts.append('        </div>')
                current_time_item = None
            
            # Iniciar resumen diario
            html_parts.append('    </div>')
            html_parts.append('    <div class="daily-summary mt-4">')
            html_parts.append('        <h6><i class="fas fa-calculator text-info"></i> Total Diario</h6>')
            html_parts.append('        <div class="macros-distribution">')
            
            # Procesar líneas de resumen
            summary_line = line.replace('•', '').strip()
            badge_class = _get_macro_badge_class(summary_line)
            html_parts.append(f'            <small class="badge {badge_class}">{summary_line}</small>')
            
    # Cerrar último item si existe
    if current_time_item:
        if current_macros:
            html_parts.append('                <div class="macros-distribution">')
            for macro in current_macros:
                badge_class = _get_macro_badge_class(macro)
                html_parts.append(f'                    <small class="badge {badge_class}">{macro}</small>')
            html_parts.append('                </div>')
        html_parts.append('            </div>')
        html_parts.append('        </div>')
        html_parts.append('    </div>')
    
    html_parts.append('</div>')
    return '\n'.join(html_parts)


def _convert_text_to_tabla_equivalencias_html(lines):
    """
    Convierte texto de tabla de equivalencias a HTML estructurado
    """
    html_parts = []
    html_parts.append('<div class="tabla-equivalencias">')
    
    current_section = None
    current_items = []
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('==='):
            continue
            
        if line.startswith('📋'):
            # Cerrar sección anterior
            if current_section and current_items:
                html_parts.append('    <div class="row">')
                
                # Dividir items en dos columnas
                mid = len(current_items) // 2
                col1_items = current_items[:mid]
                col2_items = current_items[mid:]
                
                html_parts.append('        <div class="col-md-6">')
                html_parts.append('            <ul class="list-unstyled">')
                for item in col1_items:
                    html_parts.append(f'                <li>{item}</li>')
                html_parts.append('            </ul>')
                html_parts.append('        </div>')
                
                html_parts.append('        <div class="col-md-6">')
                html_parts.append('            <ul class="list-unstyled">')
                for item in col2_items:
                    html_parts.append(f'                <li>{item}</li>')
                html_parts.append('            </ul>')
                html_parts.append('        </div>')
                html_parts.append('    </div>')
            
            # Iniciar nueva sección
            section_title = line.replace('📋', '').strip()
            icon = _get_section_icon(section_title)
            class_attr = ' class="mt-4"' if current_section else ''
            html_parts.append(f'    <h4{class_attr}><i class="{icon}"></i> {section_title}</h4>')
            current_section = section_title
            current_items = []
            
        elif line.startswith('  •'):
            # Item de equivalencia
            item = line.replace('  •', '•').strip()
            current_items.append(item)
    
    # Cerrar última sección
    if current_section and current_items:
        html_parts.append('    <div class="row">')
        
        mid = len(current_items) // 2
        col1_items = current_items[:mid]
        col2_items = current_items[mid:]
        
        html_parts.append('        <div class="col-md-6">')
        html_parts.append('            <ul class="list-unstyled">')
        for item in col1_items:
            html_parts.append(f'                <li>{item}</li>')
        html_parts.append('            </ul>')
        html_parts.append('        </div>')
        
        html_parts.append('        <div class="col-md-6">')
        html_parts.append('            <ul class="list-unstyled">')
        for item in col2_items:
            html_parts.append(f'                <li>{item}</li>')
        html_parts.append('            </ul>')
        html_parts.append('        </div>')
        html_parts.append('    </div>')
    
    html_parts.append('</div>')
    return '\n'.join(html_parts)


def _convert_text_to_formatted_html(text_content):
    """
    Convierte texto plano a HTML básico preservando formato
    """
    # Envolvemos cada línea en un párrafo
    lines = text_content.split('\n')
    wrapped_lines = ['<p>' + line.strip() + '</p>' for line in lines if line.strip()]
    return '<div class="text-content">' + ''.join(wrapped_lines) + '</div>'


def _get_meal_icon(meal_name):
    """Retorna el icono apropiado para cada comida"""
    meal_name_lower = meal_name.lower()
    if 'desayuno' in meal_name_lower:
        return 'fas fa-coffee text-warning'
    elif 'almuerzo' in meal_name_lower:
        return 'fas fa-utensils text-info'
    elif 'cena' in meal_name_lower:
        return 'fas fa-drumstick-bite text-secondary'
    elif 'merienda' in meal_name_lower:
        if 'matutina' in meal_name_lower:
            return 'fas fa-apple-alt text-success'
        else:
            return 'fas fa-cookie-bite text-danger'
    else:
        return 'fas fa-utensils text-primary'


def _get_macro_badge_class(macro_text):
    """Retorna la clase CSS apropiada para cada macronutriente"""
    macro_lower = macro_text.lower()
    if 'carbohidrato' in macro_lower:
        return 'bg-primary me-1'
    elif 'proteína' in macro_lower:
        return 'bg-success me-1'
    elif 'grasa' in macro_lower:
        return 'bg-warning text-dark me-1'
    elif 'kcal' in macro_lower or 'caloría' in macro_lower:
        return 'bg-danger'
    else:
        return 'bg-secondary me-1'


def _get_section_icon(section_title):
    """Retorna el icono apropiado para cada sección de equivalencias"""
    title_lower = section_title.lower()
    if 'carbohidrato' in title_lower:
        return 'fas fa-bread-slice text-primary'
    elif 'proteína' in title_lower:
        return 'fas fa-drumstick-bite text-success'
    elif 'grasa' in title_lower:
        return 'fas fa-seedling text-warning'
    else:
        return 'fas fa-circle text-info'


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
            
            # Para plan de comidas y tabla de equivalencias, guardar como texto con formato básico
            if request.POST.get('plan_comidas'):
                plan_text = request.POST.get('plan_comidas')
                # Conservar como texto con formato básico HTML para visualización
                valoracion.plan_comidas = _convert_text_to_formatted_html(plan_text)
            if request.POST.get('tabla_equivalencias'):
                tabla_text = request.POST.get('tabla_equivalencias')
                # Conservar como texto con formato básico HTML para visualización
                valoracion.tabla_equivalencias = _convert_text_to_formatted_html(tabla_text)
            
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
    
    # Convertir HTML a texto legible para la edición
    plan_comidas_texto = html_to_readable_text(valoracion.plan_comidas) if valoracion.plan_comidas else ''
    tabla_equivalencias_texto = html_to_readable_text(valoracion.tabla_equivalencias) if valoracion.tabla_equivalencias else ''
    
    return render(request, 'valoraciones/editar.html', {
        'valoracion': valoracion,
        'plan_comidas_texto': plan_comidas_texto,
        'tabla_equivalencias_texto': tabla_equivalencias_texto
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
