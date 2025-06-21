#!/bin/bash

# Esperar a que la base de datos esth disponible
echo "Esperando a que la base de datos esté disponible..."
while ! pg_isready -h db -p 5432 -U postgres; do
  echo "Base de datos no disponible, esperando..."
  sleep 2
done
echo "Base de datos disponible!"

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear superusuario si no existe (opcional)
echo "Verificando superusuario..."
python manage.py shell -c "
from usuarios.models import Usuario
if not Usuario.objects.filter(username='admin').exists():
    Usuario.objects.create_superuser('admin', 'admin@test.com', 'admin123', tipo='admin')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"

# Iniciar el servidor
echo "Iniciando servidor Django..."
exec "$@"

