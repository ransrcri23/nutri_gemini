from django.contrib import admin
from .models import Valoracion
from pacientes.models import Paciente


class ValoracionAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'peso_kg', 'tiene_macronutrientes', 'paciente_activo', 'fecha_creacion')
    list_filter = ('fecha_creacion', 'paciente__activo', 'paciente__nombre')
    search_fields = ('paciente__nombre', 'paciente__apellidos')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'tiene_macronutrientes')
    
    fieldsets = (
        ('Paciente', {
            'fields': ('paciente',)
        }),
        ('Mediciones Físicas', {
            'fields': ('peso_kg', 'kg_grasa', 'kg_proteinas', 'kg_minerales', 'litros_agua')
        }),
        ('Macronutrientes (Calculados por Gemini)', {
            'fields': ('carbohidratos_g', 'proteinas_g', 'grasas_g', 'calorias_totales', 'recomendaciones'),
            'classes': ('collapse',),
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )
    
    def paciente_activo(self, obj):
        """Muestra si el paciente está activo"""
        return obj.paciente.activo
    paciente_activo.boolean = True
    paciente_activo.short_description = 'Paciente Activo'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "paciente":
            # Nutricionistas y administradores ven todos los pacientes
            if hasattr(request.user, 'tipo_usuario'):
                from usuarios.models import TipoUsuario
                if request.user.tipo_usuario in [TipoUsuario.NUTRICIONISTA, TipoUsuario.ADMINISTRADOR]:
                    kwargs["queryset"] = Paciente.objects.all()
                else:
                    kwargs["queryset"] = Paciente.objects.filter(activo=True)
            else:
                kwargs["queryset"] = Paciente.objects.filter(activo=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('paciente')
        # Nutricionistas y administradores ven todas las valoraciones
        if hasattr(request.user, 'tipo_usuario'):
            from usuarios.models import TipoUsuario
            if request.user.tipo_usuario in [TipoUsuario.NUTRICIONISTA, TipoUsuario.ADMINISTRADOR]:
                return qs  # Mostrar todas
        # Por defecto, mostrar solo valoraciones de pacientes activos
        return qs.filter(paciente__activo=True)
    
    def has_change_permission(self, request, obj=None):
        # Nutricionistas y administradores pueden editar todas las valoraciones
        if hasattr(request.user, 'tipo_usuario'):
            from usuarios.models import TipoUsuario
            if request.user.tipo_usuario in [TipoUsuario.NUTRICIONISTA, TipoUsuario.ADMINISTRADOR]:
                return True
        return super().has_change_permission(request, obj)


admin.site.register(Valoracion, ValoracionAdmin)
