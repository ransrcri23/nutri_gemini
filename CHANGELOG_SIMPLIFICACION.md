# Changelog - Simplificación del Sistema de Usuarios

## Resumen de Cambios

Se ha simplificado el sistema de usuarios eliminando la funcionalidad manual de vincular pacientes y implementando la generación automática de usuarios para pacientes.

## ¿Qué se eliminó?

### 1. Funcionalidad obsoleta de vincular pacientes manualmente
- **Vista eliminada**: `vincular_paciente()` en `usuarios/views.py`
- **URL eliminada**: `/usuarios/<id>/vincular-paciente/`
- **Plantilla eliminada**: `vincular_paciente.html`
- **Botones eliminados**: Enlaces "Vincular Paciente" en admin y listas

### 2. Flujo manual de activación
- **Antes**: Los pacientes debían activar su cuenta manualmente usando códigos
- **Ahora**: Los usuarios se crean automáticamente cuando nutricionistas/admins crean pacientes

## ¿Qué se agregó?

### 1. Generación automática de usuarios
- **En vistas web**: `generar_usuario_para_paciente()` en `pacientes/views.py`
- **En admin**: Override de `save_model()` en `pacientes/admin.py`
- **Acción masiva**: "Generar usuarios para pacientes seleccionados" en admin

### 2. Mejoras en la interfaz
- **Alert informativo**: Muestra credenciales del usuario recién creado
- **Columna nueva**: "Tiene Usuario" en admin de pacientes
- **Limpieza automática**: Información sensible se borra después de mostrarla

## Flujo actual

### Para Nutricionistas/Administradores:
1. Crear paciente desde web o admin
2. → Sistema genera automáticamente:
   - Usuario con username único
   - Contraseña temporal aleatoria
   - Código de acceso único
   - PerfilPaciente vinculado
3. Se muestra información para entregar al paciente
4. Paciente puede acceder con su código de acceso

### Para Pacientes:
- **Antes**: Debían registrarse con código de activación
- **Ahora**: Reciben credenciales listas del nutricionista

## Migración de datos existentes

Para pacientes existentes sin usuarios asociados, ejecutar:

```bash
python manage.py shell < generar_usuarios_pacientes.py
```

Este script:
- Identifica pacientes sin usuarios
- Genera usuarios automáticamente
- Reporta resultados y errores

## Archivos modificados

### Eliminados:
- `usuarios/templates/usuarios/vincular_paciente.html`

### Modificados:
- `pacientes/views.py` - Generación automática
- `pacientes/admin.py` - Mejoras en admin
- `usuarios/views.py` - Eliminación de funciones obsoletas
- `usuarios/urls.py` - Eliminación de URL obsoleta
- `usuarios/templates/usuarios/detalle_usuario.html` - UI actualizada
- `usuarios/templates/usuarios/lista_usuarios.html` - Botón eliminado
- `pacientes/templates/pacientes/paciente_detalle.html` - Alert de usuario creado

### Creados:
- `generar_usuarios_pacientes.py` - Script de migración
- `pacientes/templates/pacientes/editar_paciente.html` - Edición completa
- `pacientes/templates/pacientes/lista_todos.html` - Vista para nutricionistas
- `valoraciones/templates/valoraciones/editar.html` - Edición de valoraciones
- `valoraciones/templates/valoraciones/lista_todas.html` - Vista para nutricionistas
- `valoraciones/templates/valoraciones/paciente_todas.html` - Valoraciones completas

## Verificación

Para verificar que todo funciona:

1. **Sistema check**: `python manage.py check` ✓
2. **Crear paciente como nutricionista**: Debe generar usuario automáticamente
3. **Admin**: Verificar columna "Tiene Usuario" y acción masiva
4. **Funciones obsoletas**: No deben aparecer enlaces de "Vincular Paciente"

## Beneficios

✓ **Simplicidad**: Eliminación de pasos manuales innecesarios
✓ **Eficiencia**: Flujo de trabajo más rápido para nutricionistas
✓ **Seguridad**: Generación automática de credenciales fuertes
✓ **Experiencia**: Mejor UX tanto para nutricionistas como pacientes
✓ **Mantenimiento**: Código más limpio y menos propenso a errores

