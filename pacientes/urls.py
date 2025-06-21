from django.urls import path
from . import views

urlpatterns = [
    # Vista principal
    path('', views.home, name='home'),
    
    # Gestión de pacientes (nuevas URLs)
    path('lista/', views.lista_pacientes, name='lista_pacientes'),
    path('crear/', views.crear_paciente, name='crear_paciente'),
    path('<int:paciente_id>/', views.detalle_paciente, name='detalle_paciente'),
    
    # Gestión para nutricionistas y administradores
    path('todos/', views.lista_pacientes_todos, name='lista_pacientes_todos'),
    path('<int:paciente_id>/editar/', views.editar_paciente, name='editar_paciente'),
    path('<int:paciente_id>/desactivar/', views.desactivar_paciente, name='desactivar_paciente'),
    path('<int:paciente_id>/reactivar/', views.reactivar_paciente, name='reactivar_paciente'),
    
    # URLs legacy para compatibilidad
    path('detalle/<int:pk>/', views.paciente_detalle, name='paciente_detalle'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
]
