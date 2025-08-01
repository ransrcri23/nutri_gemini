# 🥗 Nutri Gemini

Sistema inteligente de gestión nutricional que utiliza **Google Gemini AI** para generar planes alimentarios personalizados, calcular macronutrientes y crear tablas de equivalencias adaptadas a cada paciente.

## ✨ Funcionalidades

- 🧠 **Cálculo inteligente de macronutrientes** con Gemini AI
- 📋 **Planes de comidas personalizados** con horarios y distribución nutricional
- 📊 **Tablas de equivalencias alimentarias** adaptadas por paciente
- 📈 **Gráficas** de progreso de pacientes
- 👥 **Gestión completa de pacientes** con valoraciones corporales
- 📈 **Dashboard interactivo** para administradores, nutricionistas y pacientes
- ♿ **Modo alto contraste** para accesibilidad

## 🏗️ Arquitectura

- **Backend**: Django 5.2.2 + Python
- **AI**: Google Gemini AI
- **Base de datos**: PostgreSQL
- **Frontend**: Bootstrap 5 + JavaScript
- **Contenedores**: Docker + Docker Compose

## 🚀 Guía de ejecución

1. **Clonar y configurar**
   ```bash
   git clone https://github.com/ransrcri23/nutri_gemini.git
   cd nutri_gemini
   cp example.env .env  # Luego editar .env con tus credenciales
   ```

2. **Configurar variables en .env**
   - `GOOGLE_API_KEY`: [Obtener desde Google AI Studio](https://makersuite.google.com/app/apikey)
   - `DATABASE_URL`: Tu URL de PostgreSQL

3. **Ejecutar con Docker**
   ```bash
   docker-compose up --build
   ```

4. **Acceder a la aplicación**
   - URL: http://localhost:8000
   - Admin: `admin@nutricion.com` / `admin123`

5. **Detener** (cuando termines)
   ```bash
   docker-compose down
   ```

## Disclaimers

- **Configuración requerida**: Debes configurar tus propias credenciales en `.env`
- **API Key**: Necesitas una `GOOGLE_API_KEY` válida para que funcione la IA
- **Base de datos**: Requiere una instancia PostgreSQL configurada en `DATABASE_URL`
- **Primera ejecución**: Puede tomar varios minutos descargar dependencias

**Nota:** [En este enlace](https://drive.google.com/drive/folders/1IXyiHmwqJEmgfS1ljhErB8-k6-_U0CxS?usp=drive_link) puedes solicitar acceso para descargar el archivo `.env` con el `GOOGLE_API_KEY` y `DATABASE_URL` de los desarrolladores de Nutri Gemini, así como una lista de credenciales para usuarios de prueba.

*La aprobación de acceso a estas credenciales queda a discreción de los colaboradores de este proyecto.*


