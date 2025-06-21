from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, PerfilNutricionista, PerfilPaciente, TipoUsuario


class PerfilNutricionistaInline(admin.StackedInline):
    model = PerfilNutricionista
    can_delete = False
    verbose_name_plural = 'Perfil de Nutricionista'


class PerfilPacienteInline(admin.StackedInline):
    model = PerfilPaciente
    can_delete = False
    verbose_name_plural = 'Perfil de Paciente'


class UsuarioAdmin(BaseUserAdmin):
    list_display = ('email', 'nombre_completo', 'tipo_usuario', 'activo', 'fecha_creacion')
    list_filter = ('tipo_usuario', 'activo', 'is_staff', 'fecha_creacion')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('-fecha_creacion',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'telefono', 'fecha_nacimiento')}),
        ('Permisos', {
            'fields': ('tipo_usuario', 'activo', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'tipo_usuario', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    def get_inline_instances(self, request, obj=None):
        inlines = []
        if obj and obj.tipo_usuario == TipoUsuario.NUTRICIONISTA:
            inlines.append(PerfilNutricionistaInline(self.model, self.admin_site))
        elif obj and obj.tipo_usuario == TipoUsuario.PACIENTE:
            inlines.append(PerfilPacienteInline(self.model, self.admin_site))
        return inlines


class PerfilNutricionistaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'numero_colegiado', 'especialidad', 'años_experiencia')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'numero_colegiado', 'especialidad')
    list_filter = ('especialidad', 'años_experiencia')


class PerfilPacienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'paciente', 'tiene_datos_medicos')
    search_fields = ('usuario__first_name', 'usuario__last_name', 'usuario__email')
    list_filter = ('usuario__tipo_usuario', 'usuario__activo')
    
    def tiene_datos_medicos(self, obj):
        """Indica si el perfil tiene datos médicos asociados"""
        return obj.paciente is not None
    tiene_datos_medicos.boolean = True
    tiene_datos_medicos.short_description = 'Tiene Datos Médicos'

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(PerfilNutricionista, PerfilNutricionistaAdmin)
admin.site.register(PerfilPaciente, PerfilPacienteAdmin)
