#!/bin/bash

# Script de inicio automatizado para Nutri Gemini
echo "🥗 Iniciando Nutri Gemini..."

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker no está instalado"
    echo "📥 Instala Docker desde: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Verificar que Docker Compose esté disponible
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Error: Docker Compose no está disponible"
    exit 1
fi

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "📝 Configurando variables de entorno..."
    cp example.env .env
    echo "✅ Archivo .env creado desde example.env"
else
    echo "✅ Archivo .env ya existe"
fi

# Verificar si Docker Desktop está corriendo
if ! docker info &> /dev/null; then
    echo "❌ Error: Docker no está corriendo"
    echo "🔄 Inicia Docker Desktop y vuelve a ejecutar este script"
    exit 1
fi

# Parar contenedores existentes si los hay
echo "🛑 Deteniendo contenedores existentes..."
docker-compose down 2>/dev/null

# Construir e iniciar la aplicación
echo "🏗️  Construyendo e iniciando la aplicación..."
echo "⏳ Esto puede tomar unos minutos la primera vez..."

if docker-compose up --build -d; then
    echo ""
    echo "🎉 ¡Nutri Gemini iniciado exitosamente!"
    echo ""
    echo "📋 Información de acceso:"
    echo "   🌐 URL: http://localhost:8000"
    echo "   👤 Usuario: admin@nutricion.com"
    echo "   🔑 Contraseña: admin123"
    echo ""
    echo "📊 Para ver logs: docker-compose logs -f"
    echo "🛑 Para detener: docker-compose down"
    echo ""
    echo "⏳ Esperando que la aplicación esté lista..."
    
    # Esperar a que la aplicación responda
    for i in {1..30}; do
        if curl -s http://localhost:8000 > /dev/null 2>&1; then
            echo "✅ Aplicación lista!"
            break
        fi
        echo "   Intento $i/30..."
        sleep 2
    done
    
    # Abrir navegador si está disponible
    if command -v start &> /dev/null; then
        # Windows
        start http://localhost:8000
    elif command -v open &> /dev/null; then
        # macOS
        open http://localhost:8000
    elif command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open http://localhost:8000
    fi
    
else
    echo "❌ Error al iniciar la aplicación"
    echo "📋 Revisa los logs con: docker-compose logs"
    exit 1
fi
