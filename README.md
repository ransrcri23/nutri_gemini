# Nutri Gemini 🥗

Sistema de gestión nutricional con inteligencia artificial usando Django y Google Gemini AI.

## Instalación y Ejecución

### Prerrequisitos
- **Docker Desktop**: https://www.docker.com/products/docker-desktop/
- **Git**: https://git-scm.com/downloads

### Pasos para ejecutar

1. **Clonar el proyecto**
   ```bash
   git clone https://github.com/ransrcri23/nutri_gemini.git
   cd nutri_gemini
   ```

2. **Configurar variables de entorno**
   ```bash
   # En Windows (PowerShell/CMD)
   copy example.env .env
   
   # En Linux/Mac
   cp example.env .env
   ```
   
   ⚠️ **IMPORTANTE**: Debes configurar tus propias credenciales en el archivo `.env`:
   
   - **GOOGLE_API_KEY**: Obtén tu API key desde [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **SECRET_KEY**: Genera una clave desde [Django Secret Key Generator](https://djecrety.ir/)
   - **DATABASE_URL**: Configura tu base de datos PostgreSQL
   
   📖 Ver [SECURITY_SETUP.md](SECURITY_SETUP.md) para instrucciones detalladas.

3. **Iniciar la aplicación**
   ```bash
   docker-compose up --build
   ```
   
   La primera vez tomará unos minutos para descargar dependencias.

4. **Acceder a la aplicación**
   - **URL**: http://localhost:8000
   - **Usuario Administrador**: `admin@nutricion.com`
   - **Contraseña**: `admin123`

### Comandos básicos

```bash
# Detener la aplicación
docker-compose down

# Ver logs en tiempo real
docker-compose logs -f

# Reconstruir completamente
docker-compose down
docker-compose up --build

# Ejecutar comandos Django dentro del contenedor
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py shell
```

## Características

- ✅ **Modo Alto Contraste** - Accesibilidad completa
- ✅ **Cálculo de Macronutrientes** - Usando Gemini AI
- ✅ **Plan de Comidas Personalizado** - Horarios y distribución
- ✅ **Tabla de Equivalencias** - Alimentos personalizados
- ✅ **Gestión de Pacientes** - Valoraciones corporales
- ✅ **Dashboard Interactivo** - Para nutricionistas y pacientes

## Arquitectura

- **Backend**: Django 5.2.2
- **Base de Datos**: PostgreSQL (Railway)
- **AI**: Google Gemini AI
- **Frontend**: Bootstrap 5 + JavaScript
- **Contenedor**: Docker + Docker Compose

## Solución de Problemas

### Puerto 8000 ocupado
```bash
# Verificar qué proceso usa el puerto
netstat -ano | findstr :8000

# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Usar puerto 8001 local
```

### Problemas de permisos
```bash
# Limpiar y reconstruir
docker-compose down -v
docker system prune -f
docker-compose up --build
```

### Base de datos
La aplicación usa PostgreSQL en Railway (nube), no necesita configuración local.

