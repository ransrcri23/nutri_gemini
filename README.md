# Sistema de Nutrición Asistente

Sistema de gestión nutricional con generación automática de valoraciones y planes de comidas usando Gemini AI.

## Características

- Gestión de usuarios (nutricionistas, administradores) y pacientes
- Valoraciones nutricionales con cálculo automático de macronutrientes
- Generación automática de planes de comidas personalizados
- Tablas de equivalencias funcionales
- Integración con Gemini AI para generación de contenido

## Instalación y Ejecución con Docker

### Prerrequisitos

1. **Docker Desktop para Windows**
   - Descargar desde: https://www.docker.com/products/docker-desktop/
   - Instalar y reiniciar el sistema
   - Asegurarse de que Docker Desktop esté ejecutándose

### Configuración

1. **Clonar o descargar el proyecto**
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd nutricion_asistente
   ```

2. **Configurar variables de entorno**
   
   a) Copia el archivo de configuración:
   ```bash
   copy example.env .env
   ```
   
   b) **IMPORTANTE**: Edita el archivo `.env` y reemplaza:
   ```
   GOOGLE_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY_HERE
   ```
   
   Con tu clave de API de Google Gemini:
   ```
   GOOGLE_API_KEY=tu_clave_real_aqui
   ```
   
   **¿Cómo obtener la API key?**
   - Ve a: https://makersuite.google.com/app/apikey
   - Crea una cuenta gratuita de Google si no tienes
   - Genera una nueva API key
   - Cópiala y pégala en el archivo `.env`

### Ejecución

1. **Abrir PowerShell** en la carpeta del proyecto

2. **Iniciar el sistema**
   ```bash
   docker-compose up
   ```

3. **Crear usuario administrador** (solo la primera vez)
   ```bash
   docker-compose exec web python manage.py shell -c "from usuarios.models import Usuario, TipoUsuario; u = Usuario(username='admin', email='admin@test.com', first_name='Admin', last_name='User', tipo_usuario=TipoUsuario.ADMINISTRADOR); u.set_password('admin123'); u.save(); print('Usuario admin creado')"
   ```

4. **Acceder a la aplicación**
   - URL: http://localhost:8000
   - Email: `admin@test.com`
   - Contraseña: `admin123`

## Comandos Útiles

```bash
# Iniciar el sistema
docker-compose up

# Iniciar en segundo plano
docker-compose up -d

# Detener el sistema
docker-compose down

# Ver logs
docker-compose logs -f

# Reconstruir contenedores
docker-compose up --build

# Limpiar datos y reiniciar
docker-compose down -v
docker-compose up --build

# Ejecutar comandos Django
docker-compose exec web python manage.py [comando]

# Acceder al shell del contenedor
docker-compose exec web bash
```

## Estructura del Sistema

### Módulos
- **usuarios/**: Gestión de usuarios y autenticación
- **pacientes/**: Gestión de pacientes
- **valoraciones/**: Valoraciones nutricionales y generación de contenido

### Base de Datos
- En Docker: PostgreSQL local en contenedor (puerto 5433)
- En desarrollo: Railway PostgreSQL (configurado en .env)
- Datos persistentes en volúmenes Docker

## Archivos de Configuración

### Variables de Entorno (.env)

El archivo `.env` incluye todas las configuraciones necesarias:

- **GOOGLE_API_KEY**: Clave compartida de Gemini AI
- **DATABASE_***: Configuración de Railway PostgreSQL
- **DEBUG**: Modo desarrollo activado
- **SECRET_KEY**: Clave secreta de Django

### Archivos Docker

- `docker-compose.yml`: Configuración de contenedores
- `Dockerfile`: Imagen de la aplicación
- `entrypoint.sh`: Script de inicialización
- `requirements.txt`: Dependencias Python
- `.dockerignore`: Archivos excluidos de la imagen

## Solución de Problemas

### Error de conexión
- Verificar que Docker Desktop esté ejecutándose
- Verificar que el archivo `.env` existe (copiado desde `example.env`)
- Esperar a que termine la inicialización (primera vez puede tomar varios minutos)
- Revisar logs: `docker-compose logs`

### Puerto ocupado
- Cambiar puerto en `docker-compose.yml` si el 8000 está ocupado
- Verificar que no haya otras instancias ejecutándose

### Problemas de base de datos
- Reiniciar contenedores: `docker-compose restart`
- Limpiar volúmenes: `docker-compose down -v`

### Error de permisos
- Ejecutar PowerShell como administrador
- Verificar que WSL2 esté habilitado en Windows

## Desarrollo Local (sin Docker)

Si prefieres desarrollo local:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Asegurarse de que .env existe
copy example.env .env

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

## Comandos Django Útiles

```bash
# Crear migraciones
docker-compose exec web python manage.py makemigrations

# Aplicar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Shell Django
docker-compose exec web python manage.py shell

# Recopilar archivos estáticos
docker-compose exec web python manage.py collectstatic
```

## Funcionalidades Principales

1. **Gestión de Pacientes**
   - Registro completo de datos antropométricos
   - Historial de valoraciones

2. **Valoraciones Nutricionales**
   - Cálculo automático de macronutrientes
   - Generación de tablas de equivalencias
   - Planes de comidas personalizados

3. **Integración AI**
   - Generación automática de contenido nutricional
   - Personalización basada en datos del paciente
   - Regeneración independiente de componentes

## Inicio Rápido (Resumen)

1. Instalar Docker Desktop
2. Clonar el proyecto
3. Ejecutar: `copy example.env .env`
4. Ejecutar: `docker-compose up`
5. Ir a: http://localhost:8000
6. Login: admin/admin123

## Notas Técnicas

- **Framework**: Django 5.2.2
- **Base de datos**: PostgreSQL 15
- **AI**: Google Gemini API
- **Containerización**: Docker + Docker Compose
- **Servidor**: Gunicorn (producción) / Django dev server (desarrollo)

---

**El sistema crea automáticamente un usuario administrador (admin/admin123) en el primer inicio.**

