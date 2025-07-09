from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import Paciente, PacienteNuevoB
from usuarios.models import TipoUsuario, Usuario, PerfilPaciente
from utils import es_nutricionista_o_admin
from datetime import date
import random
import string


def home(request):
    """Vista principal de la aplicación"""
    # Limpiar información de sesión si se solicita
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        import json
        try:
            data = json.loads(request.body)
            if data.get('clear_session') == 'usuario_recien_creado':
                if 'usuario_recien_creado' in request.session:
                    del request.session['usuario_recien_creado']
                return JsonResponse({'success': True})
        except:
            pass
    
    return render(request, 'pacientes/home.html')


@login_required
@user_passes_test(es_nutricionista_o_admin)
def lista_pacientes(request):
    """Lista todos los pacientes activos con paginación y búsqueda"""
    query = request.GET.get('q')
    pacientes = Paciente.objects.filter(activo=True).order_by('-fecha_creacion')
    
    if query:
        pacientes = pacientes.filter(
            Q(nombre__icontains=query) |
            Q(apellidos__icontains=query) |
            Q(correo_electronico__icontains=query) |
            Q(telefono__icontains=query)
        )
    
    # Paginación
    paginator = Paginator(pacientes, 12)  # 12 pacientes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pacientes/lista.html', {
        'page_obj': page_obj,
        'query': query
    })


def detalle_paciente(request, paciente_id):
    """Muestra el detalle de un paciente específico"""
    # Para nutricionistas y admins, permitir ver pacientes inactivos
    if request.user.is_authenticated and hasattr(request.user, 'tipo_usuario'):
        if request.user.tipo_usuario in [TipoUsuario.NUTRICIONISTA, TipoUsuario.ADMINISTRADOR]:
            paciente = get_object_or_404(Paciente, id=paciente_id)
        else:
            paciente = get_object_or_404(Paciente, id=paciente_id, activo=True)
    else:
        paciente = get_object_or_404(Paciente, id=paciente_id, activo=True)
    
    return render(request, 'pacientes/paciente_detalle.html', {
        'paciente': paciente
    })


def crear_paciente(request):
    """Crear un nuevo paciente"""
    if request.method == 'POST':
        try:
            # Extraer datos del formulario
            paciente = Paciente(
                nombre=request.POST.get('nombre'),
                apellidos=request.POST.get('apellidos'),
                correo_electronico=request.POST.get('correo_electronico') or None,
                telefono=request.POST.get('telefono') or None,
                fecha_nacimiento=request.POST.get('fecha_nacimiento'),
                estatura=float(request.POST.get('estatura')),
                ocupacion=request.POST.get('ocupacion'),
                deportes=request.POST.get('deportes'),
                horas_semana=request.POST.get('horas_semana'),
                alergias=request.POST.get('alergias') or '',
                condiciones_especiales=request.POST.get('condiciones_especiales') or '',
                objetivos=request.POST.get('objetivos')
            )
            
            # Guardar el paciente
            paciente.save()
            
            # Si el usuario que está creando es nutricionista o administrador, generar usuario automáticamente
            usuario_creado = None
            password_temporal = None
            codigo_acceso = None
            
            if (request.user.is_authenticated and 
                hasattr(request.user, 'tipo_usuario') and 
                request.user.tipo_usuario in [TipoUsuario.NUTRICIONISTA, TipoUsuario.ADMINISTRADOR]):
                
                try:
                    usuario_creado, password_temporal = generar_usuario_para_paciente(paciente)
                    messages.success(request, 
                        f'Paciente {paciente.nombre} {paciente.apellidos} creado exitosamente. '
                        f'Se ha generado automáticamente el usuario.')
                    
                    # Agregar información adicional para mostrar en el template
                    request.session['usuario_recien_creado'] = {
                        'username': usuario_creado.username,
                        'password': password_temporal,
                        'email': usuario_creado.email
                    }
                    
                except Exception as e:
                    messages.warning(request, 
                        f'Paciente {paciente.nombre} {paciente.apellidos} creado exitosamente, '
                        f'pero hubo un error creando su usuario: {str(e)}')
            else:
                messages.success(request, f'Paciente {paciente.nombre} {paciente.apellidos} creado exitosamente.')
            
            return redirect('detalle_paciente', paciente_id=paciente.id)
            
        except ValueError as e:
            messages.error(request, f'Error en los datos ingresados: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
    
    return render(request, 'pacientes/crear_paciente.html')


# === VISTA LEGACY PARA COMPATIBILIDAD ===
def paciente_detalle(request, pk):
    """Vista legacy para compatibilidad con URLs antiguos"""
    # Intentar encontrar en el modelo nuevo primero
    try:
        paciente = get_object_or_404(Paciente, id=pk, activo=True)
        return redirect('detalle_paciente', paciente_id=paciente.id)
    except:
        # Si no existe en el nuevo modelo, buscar en el anterior
        paciente = get_object_or_404(PacienteNuevoB, pk=pk)
        return render(request, 'pacientes/paciente_detalle.html', {'paciente': paciente})


# === FUNCIONES AUXILIARES ===

def generar_usuario_para_paciente(paciente):
    """Genera automáticamente un usuario para un paciente"""
    try:
        # Generar email único si no tiene
        if not paciente.correo_electronico:
            email = f"paciente_{paciente.id}@nutricion.local"
        else:
            email = paciente.correo_electronico
            
        # Generar username único
        base_username = f"{paciente.nombre.lower()}.{paciente.apellidos.lower().replace(' ', '.')}"
        username = base_username
        counter = 1
        
        # Asegurar que el username sea único
        while Usuario.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Generar contraseña temporal
        password_temp = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        
        # Crear usuario
        usuario = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password_temp,
            first_name=paciente.nombre,
            last_name=paciente.apellidos,
            tipo_usuario=TipoUsuario.PACIENTE,
            fecha_nacimiento=paciente.fecha_nacimiento,
            telefono=paciente.telefono
        )
        
        # Crear perfil de paciente
        perfil = PerfilPaciente.objects.create(
            usuario=usuario,
            paciente=paciente
        )
        
        return usuario, password_temp
        
    except Exception as e:
        raise Exception(f"Error creando usuario para paciente: {str(e)}")


# === FUNCIONES PARA NUTRICIONISTAS Y ADMINISTRADORES ===


@login_required
@user_passes_test(es_nutricionista_o_admin)
def editar_paciente(request, paciente_id):
    """Permite a nutricionistas y admins editar datos de pacientes"""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos del paciente
            paciente.nombre = request.POST.get('nombre')
            paciente.apellidos = request.POST.get('apellidos')
            paciente.correo_electronico = request.POST.get('correo_electronico') or None
            paciente.telefono = request.POST.get('telefono') or None
            paciente.fecha_nacimiento = request.POST.get('fecha_nacimiento')
            paciente.estatura = float(request.POST.get('estatura'))
            paciente.ocupacion = request.POST.get('ocupacion')
            paciente.deportes = request.POST.get('deportes')
            paciente.horas_semana = request.POST.get('horas_semana')
            paciente.alergias = request.POST.get('alergias') or ''
            paciente.condiciones_especiales = request.POST.get('condiciones_especiales') or ''
            paciente.objetivos = request.POST.get('objetivos')
            
            # Guardar cambios
            paciente.save()
            
            messages.success(request, f'Datos de {paciente.nombre} {paciente.apellidos} actualizados exitosamente.')
            return redirect('detalle_paciente', paciente_id=paciente.id)
            
        except ValueError as e:
            messages.error(request, f'Error en los datos ingresados: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
    
    return render(request, 'pacientes/editar_paciente.html', {
        'paciente': paciente
    })


@login_required
@user_passes_test(es_nutricionista_o_admin)
@require_http_methods(["POST"])
def desactivar_paciente(request, paciente_id):
    """Permite a nutricionistas y admins desactivar pacientes"""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    try:
        paciente.activo = False
        paciente.save()
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True,
                'message': f'Paciente {paciente.nombre} {paciente.apellidos} desactivado exitosamente.'
            })
        else:
            messages.success(request, f'Paciente {paciente.nombre} {paciente.apellidos} desactivado exitosamente.')
            return redirect('lista_pacientes')
    
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        else:
            messages.error(request, f'Error desactivando paciente: {str(e)}')
            return redirect('detalle_paciente', paciente_id=paciente_id)


@login_required
@user_passes_test(es_nutricionista_o_admin)
@require_http_methods(["POST"])
def reactivar_paciente(request, paciente_id):
    """Permite a nutricionistas y admins reactivar pacientes"""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    try:
        paciente.activo = True
        paciente.save()
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True,
                'message': f'Paciente {paciente.nombre} {paciente.apellidos} reactivado exitosamente.'
            })
        else:
            messages.success(request, f'Paciente {paciente.nombre} {paciente.apellidos} reactivado exitosamente.')
            return redirect('detalle_paciente', paciente_id=paciente_id)
    
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        else:
            messages.error(request, f'Error reactivando paciente: {str(e)}')
            return redirect('detalle_paciente', paciente_id=paciente_id)


@login_required
@user_passes_test(es_nutricionista_o_admin)
def lista_pacientes_todos(request):
    """Lista TODOS los pacientes (activos e inactivos) para nutricionistas y admins"""
    query = request.GET.get('q')
    estado = request.GET.get('estado', 'todos')  # todos, activos, inactivos
    
    pacientes = Paciente.objects.all().order_by('-fecha_creacion')
    
    # Filtrar por estado
    if estado == 'activos':
        pacientes = pacientes.filter(activo=True)
    elif estado == 'inactivos':
        pacientes = pacientes.filter(activo=False)
    
    # Filtrar por búsqueda
    if query:
        pacientes = pacientes.filter(
            Q(nombre__icontains=query) |
            Q(apellidos__icontains=query) |
            Q(correo_electronico__icontains=query) |
            Q(telefono__icontains=query)
        )
    
    # Paginación
    paginator = Paginator(pacientes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pacientes/lista_todos.html', {
        'page_obj': page_obj,
        'query': query,
        'estado': estado
    })


# === FUNCIONES PARA OAUTH (LEGACY) ===
def oauth2callback(request):
    """Vista legacy para OAuth - ya no necesaria"""
    messages.info(request, 'La funcionalidad OAuth ya no es necesaria con la nueva estructura.')
    return redirect('home')
