# Script de inicio automatizado para Nutri Gemini (Windows PowerShell)

Write-Host "🥗 Iniciando Nutri Gemini..." -ForegroundColor Green

# Verificar que Docker esté instalado
try {
    docker --version | Out-Null
} catch {
    Write-Host "❌ Error: Docker no está instalado" -ForegroundColor Red
    Write-Host "📥 Instala Docker desde: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

# Verificar que Docker Compose esté disponible
try {
    docker-compose --version | Out-Null
} catch {
    try {
        docker compose version | Out-Null
    } catch {
        Write-Host "❌ Error: Docker Compose no está disponible" -ForegroundColor Red
        exit 1
    }
}

# Crear archivo .env si no existe
if (!(Test-Path .env)) {
    Write-Host "📝 Configurando variables de entorno..." -ForegroundColor Yellow
    Copy-Item example.env .env
    Write-Host "✅ Archivo .env creado desde example.env" -ForegroundColor Green
} else {
    Write-Host "✅ Archivo .env ya existe" -ForegroundColor Green
}

# Verificar si Docker Desktop está corriendo
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Error: Docker no está corriendo" -ForegroundColor Red
    Write-Host "🔄 Inicia Docker Desktop y vuelve a ejecutar este script" -ForegroundColor Yellow
    exit 1
}

# Parar contenedores existentes si los hay
Write-Host "🛑 Deteniendo contenedores existentes..." -ForegroundColor Yellow
docker-compose down 2>$null

# Construir e iniciar la aplicación
Write-Host "🏗️  Construyendo e iniciando la aplicación..." -ForegroundColor Yellow
Write-Host "⏳ Esto puede tomar unos minutos la primera vez..." -ForegroundColor Cyan

if (docker-compose up --build -d) {
    Write-Host ""
    Write-Host "🎉 ¡Nutri Gemini iniciado exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Información de acceso:" -ForegroundColor Cyan
    Write-Host "   🌐 URL: http://localhost:8000" -ForegroundColor White
    Write-Host "   👤 Usuario: admin@nutricion.com" -ForegroundColor White
    Write-Host "   🔑 Contraseña: admin123" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Para ver logs: docker-compose logs -f" -ForegroundColor Yellow
    Write-Host "🛑 Para detener: docker-compose down" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⏳ Esperando que la aplicación esté lista..." -ForegroundColor Cyan
    
    # Esperar a que la aplicación responda
    for ($i = 1; $i -le 30; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 5 -ErrorAction Stop
            Write-Host "✅ Aplicación lista!" -ForegroundColor Green
            break
        } catch {
            Write-Host "   Intento $i/30..." -ForegroundColor Gray
            Start-Sleep -Seconds 2
        }
    }
    
    # Abrir navegador
    Start-Process "http://localhost:8000"
    
} else {
    Write-Host "❌ Error al iniciar la aplicación" -ForegroundColor Red
    Write-Host "📋 Revisa los logs con: docker-compose logs" -ForegroundColor Yellow
    exit 1
}
