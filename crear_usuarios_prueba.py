#!/usr/bin/env python
import os
import sys
import django
from datetime import date

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutricion_asistente.settings')
django.setup()

from usuarios.models import Usuario, TipoUsuario, PerfilNutricionista, PerfilPaciente
from pacientes.models import Paciente
from valoraciones.models import Valoracion
from valoraciones.services import nutricion_calculator

def crear_usuarios_prueba():
    print("👥 Creando usuarios de prueba...")
    
    # 1. Crear Nutricionista
    print("\n1️⃣ Creando nutricionista...")
    nutricionista = Usuario.objects.create_user(
        username='nutri1',
        email='nutricionista@test.com',
        password='nutri123',
        first_name='Dra. María',
        last_name='González',
        tipo_usuario=TipoUsuario.NUTRICIONISTA,
        telefono='+1234567890',
        fecha_nacimiento=date(1985, 3, 15)
    )
    
    # Crear perfil de nutricionista
    PerfilNutricionista.objects.create(
        usuario=nutricionista,
        numero_colegiado='COL-12345',
        especialidad='Nutrición Deportiva',
        años_experiencia=8,
        biografia='Especialista en nutrición deportiva con 8 años de experiencia.'
    )
    print(f"✅ Nutricionista creado: {nutricionista.email} / nutri123")
    
    # 2. Crear Paciente Usuario
    print("\n2️⃣ Creando usuario paciente...")
    paciente_user = Usuario.objects.create_user(
        username='paciente1',
        email='paciente@test.com',
        password='paciente123',
        first_name='Juan',
        last_name='Pérez',
        tipo_usuario=TipoUsuario.PACIENTE,
        telefono='+0987654321',
        fecha_nacimiento=date(1990, 7, 20)
    )
    
    # Crear perfil de paciente (sin vincular aún)
    PerfilPaciente.objects.create(
        usuario=paciente_user
    )
    print(f"✅ Paciente usuario creado: {paciente_user.email} / paciente123")
    
    # 3. Crear Paciente en el sistema (como lo hace el nutricionista)
    print("\n3️⃣ Creando registro de paciente...")
    paciente_registro = Paciente.objects.create(
        nombre='Juan',
        apellidos='Pérez Ramírez',
        correo_electronico='paciente@test.com',
        telefono='+0987654321',
        fecha_nacimiento=date(1990, 7, 20),
        estatura=1.75,
        ocupacion='Ingeniero de Software',
        deportes='Natación, Ciclismo',
        horas_semana='6-8 horas',
        alergias='Ninguna conocida',
        condiciones_especiales='Ninguna',
        objetivos='Aumentar masa muscular y mejorar rendimiento deportivo'
    )
    print(f"✅ Paciente registrado: {paciente_registro.nombre} {paciente_registro.apellidos}")
    
    # 4. Vincular usuario paciente con registro
    print("\n4️⃣ Vinculando usuario con registro de paciente...")
    perfil_paciente = paciente_user.perfil_paciente
    perfil_paciente.paciente = paciente_registro
    perfil_paciente.save()
    print(f"✅ Vinculación completada. Código de acceso: {perfil_paciente.codigo_acceso}")
    
    # 5. Crear valoración de ejemplo
    print("\n5️⃣ Creando valoración de ejemplo...")
    valoracion = Valoracion.objects.create(
        paciente=paciente_registro,
        peso_kg=78.0,
        kg_grasa=12.0,
        kg_proteinas=48.0,
        kg_minerales=3.5,
        litros_agua=14.5,
        notas='Primera valoración. Paciente en buena condición física general.'
    )
    
    # 6. Calcular macronutrientes con Gemini
    print("\n6️⃣ Calculando macronutrientes con Gemini...")
    try:
        valoracion_actualizada = nutricion_calculator.actualizar_valoracion_con_macros(valoracion)
        print(f"✅ Macronutrientes calculados:")
        print(f"   - Carbohidratos: {valoracion_actualizada.carbohidratos_g}g")
        print(f"   - Proteínas: {valoracion_actualizada.proteinas_g}g")
        print(f"   - Grasas: {valoracion_actualizada.grasas_g}g")
        print(f"   - Calorías: {valoracion_actualizada.calorias_totales} kcal")
    except Exception as e:
        print(f"⚠️  Error calculando macronutrientes: {e}")
        print("    (La valoración se creó sin macronutrientes)")
    
    print("\n🎉 ¡Usuarios de prueba creados exitosamente!")
    print("\n🔑 Credenciales para probar:")
    print("   👑 Administrador: admin@nutricion.com / admin123")
    print("   👩‍⚕️ Nutricionista: nutricionista@test.com / nutri123")
    print("   👤 Paciente: paciente@test.com / paciente123")
    print("\n🌎 Accede en: http://127.0.0.1:8002/auth/login/")

if __name__ == "__main__":
    try:
        crear_usuarios_prueba()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

