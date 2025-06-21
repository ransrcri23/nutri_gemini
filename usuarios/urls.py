from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # Página de inicio
    path('', views.home_view, name='home'),
    
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Gestión de usuarios (solo administradores)
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:usuario_id>/', views.detalle_usuario, name='detalle_usuario'),
    path('usuarios/<int:usuario_id>/toggle/', views.toggle_usuario_activo, name='toggle_usuario_activo'),
    
    # Creación especializada de usuarios (solo administradores)
    path('usuarios/crear-nutricionista/', views.crear_nutricionista, name='crear_nutricionista'),
    path('usuarios/crear-administrador/', views.crear_administrador, name='crear_administrador'),
    
    # Vistas para pacientes
    path('mis-valoraciones/', views.mis_valoraciones, name='mis_valoraciones'),
    path('mi-valoracion/<int:valoracion_id>/', views.mi_valoracion_detalle, name='mi_valoracion_detalle'),
]

