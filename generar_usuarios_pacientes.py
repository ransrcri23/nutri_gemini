#!/usr/bin/env python
"""
Script para generar usuarios automáticamente para pacientes existentes
que no tengan un usuario asociado.

Ejecutar con: python manage.py shell < generar_usuarios_pacientes.py
"""

import os
import django
import random
import string

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutricion_asistente.settings')
django.setup()

from pacientes.models import Paciente
from usuarios.models import Usuario, TipoUsuario, PerfilPaciente

def generar_usuarios_para_pacientes_existentes():
    """Genera usuarios para todos los pacientes que no tengan uno"""
    
    print("Iniciando generación de usuarios para pacientes existentes...")
    
    # Obtener todos los pacientes
    pacientes = Paciente.objects.all()
    usuarios_creados = 0
    errores = 0
    ya_tienen_usuario = 0
    
    for paciente in pacientes:
        try:
            # Verificar si ya tiene usuario
            if hasattr(paciente, 'usuario_paciente') and paciente.usuario_paciente:
                ya_tienen_usuario += 1
                print(f"  - {paciente.nombre} {paciente.apellidos}: Ya tiene usuario")
                continue
        except:
            pass
        
        try:
            print(f"  Creando usuario para: {paciente.nombre} {paciente.apellidos}")
            
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
            
            print(f"    ✓ Usuario creado - Username: {username}, Email: {usuario.email}")
            usuarios_creados += 1
            
        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
            errores += 1
    
    print(f"\n=== RESUMEN ===")
    print(f"Pacientes que ya tenían usuario: {ya_tienen_usuario}")
    print(f"Usuarios creados exitosamente: {usuarios_creados}")
    print(f"Errores encontrados: {errores}")
    print(f"Total de pacientes procesados: {len(pacientes)}")
    
    if usuarios_creados > 0:
        print("\n⚠️  IMPORTANTE:")
        print("Los usuarios han sido creados con contraseñas temporales aleatorias.")
        print("Los pacientes podrán acceder usando su email y contraseña temporal.")
        print("Se recomienda que cambien sus contraseñas en el primer acceso.")

if __name__ == "__main__":
    generar_usuarios_para_pacientes_existentes()

