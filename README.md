# Sistema de Nutrición Asistente

## Instalación y Ejecución

### Prerrequisitos
- Docker Desktop para Windows: https://www.docker.com/products/docker-desktop/

### Pasos para ejecutar

1. **Clonar el proyecto**
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd nutricion_asistente
   ```

2. **Configurar variables de entorno**
   ```bash
   copy example.env .env
   ```

3. **Iniciar la aplicación**
   ```bash
   docker-compose up
   ```

4. **Acceder**
   - URL: http://localhost:8000
   - Usuario: `admin@nutricion.com`
   - Contraseña: `admin123`

### Comandos básicos

```bash
# Detener
docker-compose down

# Ver logs
docker-compose logs -f

# Reconstruir
docker-compose up --build
```

