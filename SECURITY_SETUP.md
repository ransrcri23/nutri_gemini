# Configuración de Seguridad - Nutri Gemini

## ⚠IMPORTANTE - ANTES DE HACER PÚBLICO EL REPOSITORIO

Este proyecto ha sido actualizado para **eliminar todas las credenciales hardcodeadas** y usar variables de entorno seguras. 

## Cambios de Seguridad Implementados

### 1. **Variables de entorno obligatorias**
Todas las credenciales sensibles ahora se configuran mediante variables de entorno:

- `GOOGLE_API_KEY` - API key de Google Gemini AI
- `SECRET_KEY` - Clave secreta de Django  
- `DATABASE_URL` - URL completa de PostgreSQL
- `DEBUG` - Modo debug (True/False)

### 2. **Archivos modificados para seguridad**

#### `nutricion_asistente/settings.py`
- Usa `os.environ.get()` para todas las credenciales
- Configuración adaptable para desarrollo y producción
- Validación segura de variables de entorno

#### `valoraciones/services.py`
- Eliminada la API key hardcodeada de Gemini
- Validación obligatoria de `GOOGLE_API_KEY`
- Error claro si la variable no está configurada

#### `docker-compose.yml`
- Eliminadas todas las credenciales del archivo
- Usa solo variables desde `.env`
- Configuración limpia y segura

#### `example.env`
- Plantilla segura sin credenciales reales
- Instrucciones detalladas de configuración
- Enlaces a servicios para generar claves

### 3. **Protección de archivos**

#### `.gitignore`
- `.env` excluido del repositorio
- Múltiples patrones de protección
- Archivos sensibles protegidos

#### `requirements.txt`
- Agregado `python-dotenv` para cargar variables
- Todas las dependencias actualizadas

## Configuración para Desarrolladores

### Paso 1: Clonar el repositorio
```bash
git clone [tu-repositorio]
cd nutricion_asistente
```

### Paso 2: Crear archivo de entorno
```bash
# En Windows
copy example.env .env

# En Linux/Mac
cp example.env .env
```

### Paso 3: Configurar credenciales en .env

Edita el archivo `.env` y configura:

```env
# API Key de Google Gemini AI
# Obtén desde: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=tu_api_key_real_aqui

# Clave secreta de Django  
# Genera desde: https://djecrety.ir/
SECRET_KEY=tu_secret_key_real_aqui

#️ URL de base de datos PostgreSQL
DATABASE_URL=postgresql://usuario:password@host:puerto/bd

# Modo debug
DEBUG=True
```

### Paso 4: Ejecutar con Docker
```bash
docker-compose up --build
```

## Validaciones de Seguridad

### El proyecto ahora es seguro para repositorios públicos porque:

1. **Sin credenciales hardcodeadas** - Todas las claves están en variables de entorno
2. **Archivo .env protegido** - Excluido del repositorio por .gitignore
3. **Validación obligatoria** - La aplicación falla si faltan credenciales
4. **Configuración clara** - Instrucciones detalladas en example.env
5. **Separación dev/prod** - Configuración adaptable por entorno

### Verificación antes de hacer push:

```bash
# 1. Verificar que .env NO está en git
git status  # .env no debe aparecer

# 2. Verificar que example.env no tiene credenciales reales
cat example.env  # Solo debe tener placeholders

# 3. Verificar que settings.py usa variables de entorno
grep -n "os.environ.get" nutricion_asistente/settings.py

# 4. Verificar que services.py valida la API key
grep -n "GOOGLE_API_KEY" valoraciones/services.py
```

## Errores Comunes y Soluciones

### Error: "GOOGLE_API_KEY no está configurada"
**Solución:** Configura la variable `GOOGLE_API_KEY` en tu archivo `.env`

### Error: "SECRET_KEY no configurada"  
**Solución:** Genera una clave en https://djecrety.ir/ y agrégala a `.env`

### Error: "Database connection failed"
**Solución:** Verifica que `DATABASE_URL` esté correctamente configurada

### Error: "No module named 'dotenv'"
**Solución:** Instala dependencias: `pip install -r requirements.txt`

## 📋 Checklist de Seguridad Pre-Público

Antes de hacer público el repositorio, verifica:

- [ ]  Archivo `.env` en `.gitignore`
- [ ]  Sin credenciales hardcodeadas en código
- [ ]  `example.env` solo con placeholders
- [ ]  Todas las variables usan `os.environ.get()`
- [ ]  Validación de variables obligatorias
- [ ]  Documentación de configuración clara
- [ ]  docker-compose.yml sin credenciales
- [ ]  requirements.txt con python-dotenv

## Mejores Prácticas de Seguridad

1. **Nunca commites archivos .env**
2. **Usa claves diferentes para dev/producción**  
3. **Rota las API keys regularmente**
4. **Mantén las dependencias actualizadas**
5. **Usa HTTPS en producción**
6. **Configura ALLOWED_HOSTS apropiadamente**

---

** REPOSITORIO LISTO PARA SER PÚBLICO** 

Con estos cambios, el repositorio es seguro para uso público sin exponer credenciales sensibles.
