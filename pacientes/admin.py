from django.contrib import admin
from django.contrib import messages
from .models import Paciente, PacienteNuevoB
from usuarios.models import TipoUsuario, Usuario, PerfilPaciente
import random
import string


class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'edad', 'estatura', 'activo', 'tiene_usuario', 'fecha_creacion')
    search_fields = ('nombre', 'apellidos', 'correo_electronico', 'telefono')
    list_filter = ('activo', 'ocupacion', 'fecha_creacion')
    readonly_fields = ('edad', 'fecha_creacion', 'fecha_actualizacion')
    list_editable = ('activo',)  # Permite editar el estado desde la lista
    actions = ['generar_usuarios_para_pacientes']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellidos', 'correo_electronico', 'telefono', 'fecha_nacimiento', 'estatura')
        }),
        ('Información de Estilo de Vida', {
            'fields': ('ocupacion', 'deportes', 'horas_semana')
        }),
        ('Información Médica', {
            'fields': ('alergias', 'condiciones_especiales', 'objetivos')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Nutricionistas y administradores ven todos los pacientes
        if hasattr(request.user, 'tipo_usuario'):
            from usuarios.models import TipoUsuario
            if request.user.tipo_usuario in [TipoUsuario.NUTRICIONISTA, TipoUsuario.ADMINISTRADOR]:
                return qs  # Mostrar todos
        # Por defecto, mostrar solo pacientes activos
        return qs.filter(activo=True)
    
    def has_change_permission(self, request, obj=None):
        # Nutricionistas y administradores pueden editar
        if hasattr(request.user, 'tipo_usuario'):
            from usuarios.models import TipoUsuario
            if request.user.tipo_usuario in [TipoUsuario.NUTRICIONISTA, TipoUsuario.ADMINISTRADOR]:
                return True
        return super().has_change_permission(request, obj)
    
    def tiene_usuario(self, obj):
        """Indica si el paciente ya tiene un usuario asociado"""
        try:
            return hasattr(obj, 'usuario_paciente') and obj.usuario_paciente is not None
        except:
            return False
    tiene_usuario.boolean = True
    tiene_usuario.short_description = 'Tiene Usuario'
    
    def generar_usuarios_para_pacientes(self, request, queryset):
        """Acción masiva para generar usuarios para pacientes seleccionados"""
        usuarios_creados = 0
        errores = 0
        
        for paciente in queryset:
            # Verificar si ya tiene usuario
            try:
                if hasattr(paciente, 'usuario_paciente') and paciente.usuario_paciente:
                    continue  # Ya tiene usuario
            except:
                pass
            
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
                PerfilPaciente.objects.create(
                    usuario=usuario,
                    paciente=paciente
                )
                
                usuarios_creados += 1
                
            except Exception as e:
                errores += 1
                
        if usuarios_creados > 0:
            messages.success(request, f"Se crearon {usuarios_creados} usuarios exitosamente.")
        if errores > 0:
            messages.error(request, f"Hubo {errores} errores al crear usuarios.")
    
    generar_usuarios_para_pacientes.short_description = "Generar usuarios para pacientes seleccionados"
    
    def save_model(self, request, obj, form, change):
        """Override save_model para generar usuario automáticamente al crear desde admin"""
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        
        # Si es un nuevo paciente y el usuario es admin o nutricionista, generar usuario
        if (is_new and hasattr(request.user, 'tipo_usuario') and 
            request.user.tipo_usuario in [TipoUsuario.NUTRICIONISTA, TipoUsuario.ADMINISTRADOR]):
            
            try:
                # Verificar si ya tiene usuario
                if hasattr(obj, 'usuario_paciente') and obj.usuario_paciente:
                    return
            except:
                pass
            
            try:
                # Generar email único si no tiene
                if not obj.correo_electronico:
                    email = f"paciente_{obj.id}@nutricion.local"
                else:
                    email = obj.correo_electronico
                    
                # Generar username único
                base_username = f"{obj.nombre.lower()}.{obj.apellidos.lower().replace(' ', '.')}"
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
                    first_name=obj.nombre,
                    last_name=obj.apellidos,
                    tipo_usuario=TipoUsuario.PACIENTE,
                    fecha_nacimiento=obj.fecha_nacimiento,
                    telefono=obj.telefono
                )
                
                # Crear perfil de paciente
                perfil = PerfilPaciente.objects.create(
                    usuario=usuario,
                    paciente=obj
                )
                
                messages.success(request, 
                    f"Se generó automáticamente el usuario para {obj.nombre} {obj.apellidos}. "
                    f"Email: {usuario.email}")
                
            except Exception as e:
                messages.warning(request, 
                    f"El paciente fue creado pero hubo un error generando su usuario: {str(e)}")


class PacienteNuevoBAdmin(admin.ModelAdmin):
    """DEPRECATED: Admin para el modelo anterior"""
    list_display = ('nombre', 'apellidos', 'fecha_nacimiento')
    search_fields = ('nombre', 'apellidos')
    list_filter = ('ocupacion',)


admin.site.register(Paciente, PacienteAdmin)
admin.site.register(PacienteNuevoB, PacienteNuevoBAdmin)
