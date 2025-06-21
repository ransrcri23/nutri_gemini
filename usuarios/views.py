from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Usuario, TipoUsuario, PerfilNutricionista, PerfilPaciente
from pacientes.models import Paciente
from valoraciones.models import Valoracion
from django.contrib.auth.models import Group
from datetime import date
import random
import string


# === FUNCIONES DE UTILIDAD ===
def es_administrador(user):
    """Verifica si el usuario es administrador"""
    return user.is_authenticated and user.tipo_usuario == TipoUsuario.ADMINISTRADOR

def es_nutricionista(user):
    """Verifica si el usuario es nutricionista o administrador"""
    return user.is_authenticated and user.tipo_usuario in [TipoUsuario.NUTRICIONISTA, TipoUsuario.ADMINISTRADOR]

def es_paciente(user):
    """Verifica si el usuario es paciente"""
    return user.is_authenticated and user.tipo_usuario == TipoUsuario.PACIENTE


# === VISTAS GENERALES ===
def home_view(request):
    """Página de inicio - redirige según el estado del usuario"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')


# === VISTAS DE AUTENTICACIÓN ===
def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None and user.activo:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            messages.success(request, f'¡Bienvenido {user.nombre_completo}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Credenciales inválidas o cuenta inactiva.')
    
    return render(request, 'usuarios/login.html')


def logout_view(request):
    """Vista de logout con limpieza completa de sesión"""
    if request.user.is_authenticated:
        # Limpiar la sesión completamente
        request.session.flush()
        # Logout del usuario
        logout(request)
        messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')


@login_required
def dashboard(request):
    """Dashboard principal basado en tipo de usuario"""
    user = request.user
    
    if user.tipo_usuario == TipoUsuario.ADMINISTRADOR:
        return dashboard_administrador(request)
    elif user.tipo_usuario == TipoUsuario.NUTRICIONISTA:
        return dashboard_nutricionista(request)
    elif user.tipo_usuario == TipoUsuario.PACIENTE:
        return dashboard_paciente(request)
    else:
        messages.error(request, 'Tipo de usuario no válido.')
        return redirect('login')


def dashboard_administrador(request):
    """Dashboard para administradores"""
    # Estadísticas generales
    total_usuarios = Usuario.objects.filter(activo=True).count()
    total_nutricionistas = Usuario.objects.filter(tipo_usuario=TipoUsuario.NUTRICIONISTA, activo=True).count()
    total_pacientes_usuarios = Usuario.objects.filter(tipo_usuario=TipoUsuario.PACIENTE, activo=True).count()
    total_pacientes_registros = Paciente.objects.filter(activo=True).count()
    total_valoraciones = Valoracion.objects.count()
    
    # Usuarios recientes
    usuarios_recientes = Usuario.objects.filter(activo=True).order_by('-fecha_creacion')[:5]
    
    # Valoraciones recientes
    valoraciones_recientes = Valoracion.objects.select_related('paciente').order_by('-fecha_creacion')[:5]
    
    context = {
        'total_usuarios': total_usuarios,
        'total_nutricionistas': total_nutricionistas,
        'total_pacientes_usuarios': total_pacientes_usuarios,
        'total_pacientes_registros': total_pacientes_registros,
        'total_valoraciones': total_valoraciones,
        'usuarios_recientes': usuarios_recientes,
        'valoraciones_recientes': valoraciones_recientes,
    }
    
    return render(request, 'usuarios/dashboard_administrador.html', context)


def dashboard_nutricionista(request):
    """Dashboard para nutricionistas"""
    # Estadísticas del nutricionista
    total_pacientes = Paciente.objects.filter(activo=True).count()
    total_valoraciones = Valoracion.objects.count()
    valoraciones_pendientes = Valoracion.objects.filter(
        carbohidratos_g__isnull=True
    ).count()
    
    # Pacientes y valoraciones recientes
    pacientes_recientes = Paciente.objects.filter(activo=True).order_by('-fecha_creacion')[:5]
    valoraciones_recientes = Valoracion.objects.select_related('paciente').order_by('-fecha_creacion')[:5]
    
    context = {
        'total_pacientes': total_pacientes,
        'total_valoraciones': total_valoraciones,
        'valoraciones_pendientes': valoraciones_pendientes,
        'pacientes_recientes': pacientes_recientes,
        'valoraciones_recientes': valoraciones_recientes,
    }
    
    return render(request, 'usuarios/dashboard_nutricionista.html', context)


def dashboard_paciente(request):
    """Dashboard para pacientes"""
    try:
        perfil_paciente = request.user.perfil_paciente
        if perfil_paciente.paciente:
            paciente = perfil_paciente.paciente
            valoraciones = paciente.valoraciones.all().order_by('-fecha_creacion')
            ultima_valoracion = valoraciones.first()
            
            context = {
                'paciente': paciente,
                'valoraciones': valoraciones,
                'ultima_valoracion': ultima_valoracion,
                'total_valoraciones': valoraciones.count(),
            }
        else:
            context = {
                'sin_paciente': True,
            }
    except PerfilPaciente.DoesNotExist:
        context = {
            'sin_perfil': True
        }
    
    return render(request, 'usuarios/dashboard_paciente.html', context)


# === GESTIÓN DE USUARIOS (Solo Administradores) ===
@user_passes_test(es_administrador)
def lista_usuarios(request):
    """Lista todos los usuarios del sistema"""
    query = request.GET.get('q')
    tipo_filtro = request.GET.get('tipo')
    
    usuarios = Usuario.objects.filter(activo=True).order_by('-fecha_creacion')
    
    if query:
        usuarios = usuarios.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(username__icontains=query)
        )
    
    if tipo_filtro:
        usuarios = usuarios.filter(tipo_usuario=tipo_filtro)
    
    # Paginación
    paginator = Paginator(usuarios, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'tipo_filtro': tipo_filtro,
        'tipos_usuario': TipoUsuario.choices,
    }
    
    return render(request, 'usuarios/lista_usuarios.html', context)


@user_passes_test(es_administrador)
def crear_usuario(request):
    """Crear nuevo usuario"""
    if request.method == 'POST':
        try:
            # Datos básicos
            email = request.POST.get('email')
            username = request.POST.get('username') or email
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            tipo_usuario = request.POST.get('tipo_usuario')
            telefono = request.POST.get('telefono')
            fecha_nacimiento = request.POST.get('fecha_nacimiento') or None
            
            # Verificar que el email no exista
            if Usuario.objects.filter(email=email).exists():
                messages.error(request, 'Ya existe un usuario con este email.')
                return render(request, 'usuarios/crear_usuario.html')
            
            # Crear usuario
            usuario = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                tipo_usuario=tipo_usuario,
                telefono=telefono,
                fecha_nacimiento=fecha_nacimiento
            )
            
            # Crear perfil específico según tipo
            if tipo_usuario == TipoUsuario.NUTRICIONISTA:
                PerfilNutricionista.objects.create(
                    usuario=usuario,
                    numero_colegiado=request.POST.get('numero_colegiado'),
                    especialidad=request.POST.get('especialidad'),
                    años_experiencia=int(request.POST.get('años_experiencia', 0)),
                    biografia=request.POST.get('biografia', '')
                )
            elif tipo_usuario == TipoUsuario.PACIENTE:
                PerfilPaciente.objects.create(
                    usuario=usuario
                )
            
            messages.success(request, f'Usuario {usuario.nombre_completo} creado exitosamente.')
            return redirect('lista_usuarios')
            
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
    
    return render(request, 'usuarios/crear_usuario.html', {
        'tipos_usuario': TipoUsuario.choices
    })


@user_passes_test(es_administrador)
def detalle_usuario(request, usuario_id):
    """Ver detalles de un usuario"""
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    context = {
        'usuario': usuario,
    }
    
    # Agregar información específica según tipo
    if usuario.tipo_usuario == TipoUsuario.NUTRICIONISTA:
        try:
            context['perfil_nutricionista'] = usuario.perfil_nutricionista
        except PerfilNutricionista.DoesNotExist:
            pass
    elif usuario.tipo_usuario == TipoUsuario.PACIENTE:
        try:
            context['perfil_paciente'] = usuario.perfil_paciente
        except PerfilPaciente.DoesNotExist:
            pass
    
    return render(request, 'usuarios/detalle_usuario.html', context)


@user_passes_test(es_administrador)
def toggle_usuario_activo(request, usuario_id):
    """Activar/desactivar usuario"""
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id=usuario_id)
        usuario.activo = not usuario.activo
        usuario.save()
        
        estado = 'activado' if usuario.activo else 'desactivado'
        messages.success(request, f'Usuario {usuario.nombre_completo} {estado} exitosamente.')
    
    return redirect('lista_usuarios')


# === VISTAS ESPECÍFICAS PARA PACIENTES ===
@login_required
def mis_valoraciones(request):
    """Vista para que los pacientes vean sus valoraciones"""
    if request.user.tipo_usuario != TipoUsuario.PACIENTE:
        messages.error(request, 'Acceso denegado.')
        return redirect('dashboard')
    
    try:
        perfil_paciente = request.user.perfil_paciente
        if perfil_paciente.paciente:
            valoraciones = perfil_paciente.paciente.valoraciones.all().order_by('-fecha_creacion')
            
            # Paginación
            paginator = Paginator(valoraciones, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context = {
                'page_obj': page_obj,
                'paciente': perfil_paciente.paciente,
            }
        else:
            context = {'sin_paciente': True}
    except PerfilPaciente.DoesNotExist:
        context = {'sin_perfil': True}
    
    return render(request, 'usuarios/mis_valoraciones.html', context)


@login_required
def mi_valoracion_detalle(request, valoracion_id):
    """Detalle de valoración para pacientes"""
    if request.user.tipo_usuario != TipoUsuario.PACIENTE:
        messages.error(request, 'Acceso denegado.')
        return redirect('dashboard')
    
    try:
        perfil_paciente = request.user.perfil_paciente
        if perfil_paciente.paciente:
            valoracion = get_object_or_404(
                Valoracion, 
                id=valoracion_id, 
                paciente=perfil_paciente.paciente
            )
            return render(request, 'usuarios/mi_valoracion_detalle.html', {
                'valoracion': valoracion
            })
        else:
            messages.error(request, 'No tienes un perfil de paciente asociado.')
    except PerfilPaciente.DoesNotExist:
        messages.error(request, 'No tienes un perfil de paciente.')
    
    return redirect('dashboard')


# === NOTA: FUNCIONALIDAD DE VINCULAR PACIENTES REMOVIDA ===
# Los usuarios de pacientes ahora se crean automáticamente cuando
# un nutricionista o administrador crea un paciente.
