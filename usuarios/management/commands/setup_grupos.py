from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from usuarios.models import Usuario, TipoUsuario
from pacientes.models import Paciente
from valoraciones.models import Valoracion


class Command(BaseCommand):
    help = 'Crea los grupos de usuarios y asigna permisos'
    
    def handle(self, *args, **options):
        self.stdout.write('Creando grupos de usuarios...')
        
        # Crear grupos
        administradores, created = Group.objects.get_or_create(name='Administradores')
        nutricionistas, created = Group.objects.get_or_create(name='Nutricionistas')
        pacientes, created = Group.objects.get_or_create(name='Pacientes')
        
        # Obtener content types
        usuario_ct = ContentType.objects.get_for_model(Usuario)
        paciente_ct = ContentType.objects.get_for_model(Paciente)
        valoracion_ct = ContentType.objects.get_for_model(Valoracion)
        
        # Permisos para Administradores (todos los permisos)
        admin_perms = Permission.objects.all()
        administradores.permissions.set(admin_perms)
        
        # Permisos para Nutricionistas
        nutricionista_perms = [
            # Pacientes
            Permission.objects.get(codename='add_paciente', content_type=paciente_ct),
            Permission.objects.get(codename='change_paciente', content_type=paciente_ct),
            Permission.objects.get(codename='view_paciente', content_type=paciente_ct),
            # Valoraciones
            Permission.objects.get(codename='add_valoracion', content_type=valoracion_ct),
            Permission.objects.get(codename='change_valoracion', content_type=valoracion_ct),
            Permission.objects.get(codename='view_valoracion', content_type=valoracion_ct),
            Permission.objects.get(codename='delete_valoracion', content_type=valoracion_ct),
        ]
        nutricionistas.permissions.set(nutricionista_perms)
        
        # Permisos para Pacientes (solo ver sus propias valoraciones)
        paciente_perms = [
            Permission.objects.get(codename='view_valoracion', content_type=valoracion_ct),
        ]
        pacientes.permissions.set(paciente_perms)
        
        self.stdout.write(
            self.style.SUCCESS('Grupos y permisos creados exitosamente:')
        )
        self.stdout.write(f'- Administradores: {admin_perms.count()} permisos')
        self.stdout.write(f'- Nutricionistas: {len(nutricionista_perms)} permisos')
        self.stdout.write(f'- Pacientes: {len(paciente_perms)} permisos')
        
        # Crear usuario administrador por defecto si no existe
        if not Usuario.objects.filter(tipo_usuario=TipoUsuario.ADMINISTRADOR).exists():
            admin_user = Usuario.objects.create_user(
                username='admin',
                email='admin@nutricion.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                tipo_usuario=TipoUsuario.ADMINISTRADOR
            )
            self.stdout.write(
                self.style.SUCCESS(f'Usuario administrador creado: {admin_user.email} / admin123')
            )

