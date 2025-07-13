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
import json


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
        return redirect('welcome')

def welcome_view(request):
    """Pantalla de bienvenida con información de la aplicación"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    return render(request, 'usuarios/welcome.html')


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
    return redirect('welcome')


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
    """Lista todos los usuarios del sistema (activos e inactivos)"""
    query = request.GET.get('q')
    tipo_filtro = request.GET.get('tipo')
    estado_filtro = request.GET.get('estado')
    
    usuarios = Usuario.objects.all().order_by('-fecha_creacion')
    
    if query:
        usuarios = usuarios.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(username__icontains=query)
        )
    
    if tipo_filtro:
        usuarios = usuarios.filter(tipo_usuario=tipo_filtro)
    
    if estado_filtro:
        if estado_filtro == 'activo':
            usuarios = usuarios.filter(activo=True)
        elif estado_filtro == 'inactivo':
            usuarios = usuarios.filter(activo=False)
    
    # Paginación
    paginator = Paginator(usuarios, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
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
    
    # Verificar si hay credenciales temporales en la sesión
    if 'usuario_recien_creado' in request.session:
        usuario_recien_creado = request.session['usuario_recien_creado']
        # Solo mostrar si es para este usuario específico
        if usuario_recien_creado.get('username') == usuario.username:
            context['usuario_recien_creado'] = usuario_recien_creado
    
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


# === FUNCIONES PARA CREAR USUARIOS ESPECIALIZADOS ===

def generar_usuario_para_nutricionista(datos_nutricionista):
    """Genera automáticamente un usuario para un nutricionista"""
    try:
        # Generar email único si no tiene
        if not datos_nutricionista.get('email'):
            email = f"nutricionista_{datos_nutricionista['nombre'].lower()}_{datos_nutricionista['apellidos'].lower()}@nutricion.local"
        else:
            email = datos_nutricionista['email']
            
        # Generar username único
        base_username = f"{datos_nutricionista['nombre'].lower()}.{datos_nutricionista['apellidos'].lower().replace(' ', '.')}"
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
            first_name=datos_nutricionista['nombre'],
            last_name=datos_nutricionista['apellidos'],
            tipo_usuario=TipoUsuario.NUTRICIONISTA,
            fecha_nacimiento=datos_nutricionista.get('fecha_nacimiento'),
            telefono=datos_nutricionista.get('telefono')
        )
        
        # Crear perfil de nutricionista
        perfil = PerfilNutricionista.objects.create(
            usuario=usuario,
            numero_colegiado=datos_nutricionista.get('numero_colegiado', ''),
            especialidad=datos_nutricionista.get('especialidad', ''),
            años_experiencia=int(datos_nutricionista.get('años_experiencia', 0)),
            biografia=datos_nutricionista.get('biografia', '')
        )
        
        return usuario, password_temp
        
    except Exception as e:
        raise Exception(f"Error creando usuario para nutricionista: {str(e)}")


def generar_usuario_para_administrador(datos_administrador):
    """Genera automáticamente un usuario administrador"""
    try:
        # Generar email único si no tiene
        if not datos_administrador.get('email'):
            email = f"admin_{datos_administrador['nombre'].lower()}_{datos_administrador['apellidos'].lower()}@nutricion.local"
        else:
            email = datos_administrador['email']
            
        # Generar username único
        base_username = f"{datos_administrador['nombre'].lower()}.{datos_administrador['apellidos'].lower().replace(' ', '.')}"
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
            first_name=datos_administrador['nombre'],
            last_name=datos_administrador['apellidos'],
            tipo_usuario=TipoUsuario.ADMINISTRADOR,
            fecha_nacimiento=datos_administrador.get('fecha_nacimiento'),
            telefono=datos_administrador.get('telefono')
        )
        
        return usuario, password_temp
        
    except Exception as e:
        raise Exception(f"Error creando usuario administrador: {str(e)}")


@user_passes_test(es_administrador)
def crear_nutricionista(request):
    """Crear nuevo nutricionista con generación automática de usuario"""
    if request.method == 'POST':
        try:
            # Extraer datos del formulario
            datos_nutricionista = {
                'nombre': request.POST.get('nombre'),
                'apellidos': request.POST.get('apellidos'),
                'email': request.POST.get('email'),
                'telefono': request.POST.get('telefono'),
                'fecha_nacimiento': request.POST.get('fecha_nacimiento') or None,
                'numero_colegiado': request.POST.get('numero_colegiado'),
                'especialidad': request.POST.get('especialidad'),
                'años_experiencia': request.POST.get('años_experiencia', 0),
                'biografia': request.POST.get('biografia', '')
            }
            
            # Validar campos requeridos
            if not datos_nutricionista['nombre'] or not datos_nutricionista['apellidos']:
                messages.error(request, 'El nombre y apellidos son requeridos.')
                return render(request, 'usuarios/crear_nutricionista.html')
            
            if datos_nutricionista['email'] and Usuario.objects.filter(email=datos_nutricionista['email']).exists():
                messages.error(request, 'Ya existe un usuario con este email.')
                return render(request, 'usuarios/crear_nutricionista.html')
            
            # Generar usuario automáticamente
            usuario_creado, password_temporal = generar_usuario_para_nutricionista(datos_nutricionista)
            
            messages.success(request, 
                f'Nutricionista {usuario_creado.first_name} {usuario_creado.last_name} creado exitosamente. '
                f'Se ha generado automáticamente el usuario.')
            
            # Agregar información para mostrar en el template
            request.session['usuario_recien_creado'] = {
                'username': usuario_creado.username,
                'password': password_temporal,
                'email': usuario_creado.email,
                'tipo': 'nutricionista'
            }
            
            return redirect('detalle_usuario', usuario_id=usuario_creado.id)
            
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
    
    return render(request, 'usuarios/crear_nutricionista.html')


@user_passes_test(es_administrador)
def crear_administrador(request):
    """Crear nuevo administrador con generación automática de usuario"""
    if request.method == 'POST':
        try:
            # Extraer datos del formulario
            datos_administrador = {
                'nombre': request.POST.get('nombre'),
                'apellidos': request.POST.get('apellidos'),
                'email': request.POST.get('email'),
                'telefono': request.POST.get('telefono'),
                'fecha_nacimiento': request.POST.get('fecha_nacimiento') or None
            }
            
            # Validar campos requeridos
            if not datos_administrador['nombre'] or not datos_administrador['apellidos']:
                messages.error(request, 'El nombre y apellidos son requeridos.')
                return render(request, 'usuarios/crear_administrador.html')
            
            if datos_administrador['email'] and Usuario.objects.filter(email=datos_administrador['email']).exists():
                messages.error(request, 'Ya existe un usuario con este email.')
                return render(request, 'usuarios/crear_administrador.html')
            
            # Generar usuario automáticamente
            usuario_creado, password_temporal = generar_usuario_para_administrador(datos_administrador)
            
            messages.success(request, 
                f'Administrador {usuario_creado.first_name} {usuario_creado.last_name} creado exitosamente. '
                f'Se ha generado automáticamente el usuario.')
            
            # Agregar información para mostrar en el template
            request.session['usuario_recien_creado'] = {
                'username': usuario_creado.username,
                'password': password_temporal,
                'email': usuario_creado.email,
                'tipo': 'administrador'
            }
            
            return redirect('detalle_usuario', usuario_id=usuario_creado.id)
            
        except Exception as e:
            messages.error(request, f'Error inesperado: {str(e)}')
    
    return render(request, 'usuarios/crear_administrador.html')


# === GRÁFICAS DE PROGRESO ===

@login_required
def graficas_progreso(request):
    """Vista principal de gráficas - redirige según tipo de usuario"""
    if request.user.tipo_usuario == TipoUsuario.PACIENTE:
        # Los pacientes solo ven sus propias gráficas
        try:
            perfil_paciente = request.user.perfil_paciente
            if perfil_paciente.paciente:
                return redirect('grafica_paciente', paciente_id=perfil_paciente.paciente.id)
            else:
                messages.error(request, 'No tienes un perfil de paciente asociado.')
                return redirect('dashboard')
        except PerfilPaciente.DoesNotExist:
            messages.error(request, 'No tienes un perfil de paciente.')
            return redirect('dashboard')
    else:
        # Nutricionistas y administradores ven lista de pacientes
        return lista_pacientes_graficas(request)


@login_required
def lista_pacientes_graficas(request):
    """Lista de pacientes para seleccionar gráficas (solo nutricionistas/admins)"""
    if request.user.tipo_usuario == TipoUsuario.PACIENTE:
        messages.error(request, 'Acceso denegado.')
        return redirect('dashboard')
    
    # Obtener solo pacientes que tengan al menos una valoración
    pacientes = Paciente.objects.filter(
        activo=True,
        valoraciones__isnull=False
    ).distinct().order_by('nombre', 'apellidos')
    
    # Filtro de búsqueda
    query = request.GET.get('q')
    if query:
        pacientes = pacientes.filter(
            Q(nombre__icontains=query) |
            Q(apellidos__icontains=query)
        )
    
    # Paginación
    paginator = Paginator(pacientes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'usuarios/lista_pacientes_graficas.html', {
        'page_obj': page_obj,
        'query': query
    })


@login_required
def grafica_paciente(request, paciente_id):
    """Muestra las gráficas de progreso de un paciente específico"""
    paciente = get_object_or_404(Paciente, id=paciente_id, activo=True)
    
    # Verificar permisos
    if request.user.tipo_usuario == TipoUsuario.PACIENTE:
        # Los pacientes solo pueden ver sus propias gráficas
        try:
            perfil_paciente = request.user.perfil_paciente
            if not perfil_paciente.paciente or perfil_paciente.paciente.id != paciente.id:
                messages.error(request, 'Solo puedes ver tus propias gráficas.')
                return redirect('dashboard')
        except PerfilPaciente.DoesNotExist:
            messages.error(request, 'No tienes un perfil de paciente.')
            return redirect('dashboard')
    
    # Obtener las últimas 10 valoraciones del paciente
    valoraciones = paciente.valoraciones.all().order_by('-fecha_creacion')[:10]
    
    if not valoraciones:
        messages.warning(request, f'No hay valoraciones disponibles para {paciente.nombre} {paciente.apellidos}.')
        if request.user.tipo_usuario == TipoUsuario.PACIENTE:
            return redirect('dashboard')
        else:
            return redirect('lista_pacientes_graficas')
    
    # Invertir el orden para mostrar cronológicamente (más antigua a más reciente)
    valoraciones = list(reversed(valoraciones))
    
    # Preparar datos para las gráficas
    datos_graficas = {
        'fechas': [v.fecha_creacion.strftime('%d/%m/%Y') for v in valoraciones],
        'pesos': [float(v.peso_kg) for v in valoraciones],
        'porcentajes_grasa': [round((float(v.kg_grasa) / float(v.peso_kg)) * 100, 1) for v in valoraciones],
        'porcentajes_musculo': [round((float(v.kg_proteinas) / float(v.peso_kg)) * 100, 1) for v in valoraciones],
        'kg_grasa': [float(v.kg_grasa) for v in valoraciones],
        'kg_musculo': [float(v.kg_proteinas) for v in valoraciones],
        'litros_agua': [float(v.litros_agua) for v in valoraciones],
        'kg_minerales': [float(v.kg_minerales) for v in valoraciones]
    }
    
    context = {
        'paciente': paciente,
        'valoraciones': valoraciones,
        'datos_graficas': datos_graficas,
        'total_valoraciones': len(valoraciones)
    }
    
    return render(request, 'usuarios/grafica_paciente.html', context)


# === NOTA: FUNCIONALIDAD DE VINCULAR PACIENTES REMOVIDA ===
# Los usuarios de pacientes ahora se crean automáticamente cuando
# un nutricionista o administrador crea un paciente.
