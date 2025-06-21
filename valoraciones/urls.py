from django.urls import path
from . import views

urlpatterns = [
    # Lista de valoraciones
    path('', views.lista_valoraciones, name='lista_valoraciones'),
    
    # Detalle de valoración
    path('<int:valoracion_id>/', views.detalle_valoracion, name='detalle_valoracion'),
    
    # Crear valoración para un paciente
    path('crear/<int:paciente_id>/', views.crear_valoracion, name='crear_valoracion'),
    
    # Recalcular macronutrientes
    path('<int:valoracion_id>/recalcular/', views.recalcular_macronutrientes, name='recalcular_macronutrientes'),
    path('<int:valoracion_id>/regenerar-plan/', views.regenerar_plan_comidas, name='regenerar_plan_comidas'),
    path('<int:valoracion_id>/regenerar-tabla/', views.regenerar_tabla_equivalencias, name='regenerar_tabla_equivalencias'),
    
    # Valoraciones de un paciente específico
    path('paciente/<int:paciente_id>/', views.valoraciones_paciente, name='valoraciones_paciente'),
    
    # URLs para nutricionistas y administradores
    path('todas/', views.lista_valoraciones_todas, name='lista_valoraciones_todas'),
    path('<int:valoracion_id>/editar/', views.editar_valoracion, name='editar_valoracion'),
    path('paciente/<int:paciente_id>/todas/', views.valoraciones_paciente_todas, name='valoraciones_paciente_todas'),
]

