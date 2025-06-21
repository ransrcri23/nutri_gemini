from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone


class TipoUsuario(models.TextChoices):
    ADMINISTRADOR = 'administrador', 'Administrador'
    NUTRICIONISTA = 'nutricionista', 'Nutricionista'
    PACIENTE = 'paciente', 'Paciente'


class Usuario(AbstractUser):
    """Modelo de usuario personalizado"""
    email = models.EmailField(unique=True)
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.PACIENTE
    )
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Usar email como username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def save(self, *args, **kwargs):
        # Auto-asignar grupos basado en tipo de usuario
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.asignar_grupo()
    
    def asignar_grupo(self):
        """Asigna el grupo correspondiente al usuario"""
        # Remover de todos los grupos primero
        self.groups.clear()
        
        try:
            if self.tipo_usuario == TipoUsuario.ADMINISTRADOR:
                grupo = Group.objects.get(name='Administradores')
                self.groups.add(grupo)
                self.is_staff = True
                self.is_superuser = True
            elif self.tipo_usuario == TipoUsuario.NUTRICIONISTA:
                grupo = Group.objects.get(name='Nutricionistas')
                self.groups.add(grupo)
                self.is_staff = True
            elif self.tipo_usuario == TipoUsuario.PACIENTE:
                grupo = Group.objects.get(name='Pacientes')
                self.groups.add(grupo)
                self.is_staff = False
            
            self.save(update_fields=['is_staff', 'is_superuser'])
        except Group.DoesNotExist:
            pass  # Los grupos se crearán en las migraciones
    
    @property
    def edad(self):
        """Calcula la edad del usuario"""
        if self.fecha_nacimiento:
            today = timezone.now().date()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def __str__(self):
        return f"{self.nombre_completo} ({self.get_tipo_usuario_display()})"


class PerfilNutricionista(models.Model):
    """Perfil extendido para nutricionistas"""
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='perfil_nutricionista'
    )
    numero_colegiado = models.CharField(max_length=50, unique=True)
    especialidad = models.CharField(max_length=200)
    años_experiencia = models.PositiveIntegerField()
    biografia = models.TextField(blank=True)
    # foto = models.ImageField(upload_to='nutricionistas/', blank=True, null=True)  # Deshabilitado temporalmente
    
    class Meta:
        db_table = 'perfiles_nutricionistas'
        verbose_name = 'Perfil de Nutricionista'
        verbose_name_plural = 'Perfiles de Nutricionistas'
    
    def __str__(self):
        return f"Dr(a). {self.usuario.nombre_completo} - {self.especialidad}"


class PerfilPaciente(models.Model):
    """Perfil extendido para pacientes - relacionado con el modelo Paciente existente"""
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_paciente'
    )
    paciente = models.OneToOneField(
        'pacientes.Paciente',
        on_delete=models.CASCADE,
        related_name='usuario_paciente',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'perfiles_pacientes'
        verbose_name = 'Perfil de Paciente'
        verbose_name_plural = 'Perfiles de Pacientes'
    
    def __str__(self):
        if self.paciente:
            return f"Paciente: {self.usuario.nombre_completo} - {self.paciente.nombre} {self.paciente.apellidos}"
        return f"Usuario: {self.usuario.nombre_completo} (sin datos médicos)"
