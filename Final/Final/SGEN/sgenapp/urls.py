from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin - TU PANEL PERSONALIZADO
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('admin/usuarios/crear/', views.admin_crear_usuario, name='admin_crear_usuario'),
    path('admin/usuarios/editar/<int:usuario_id>/', views.admin_editar_usuario, name='admin_editar_usuario'),
    path('admin/usuarios/eliminar/<int:usuario_id>/', views.admin_eliminar_usuario, name='admin_eliminar_usuario'),
    path('admin/reportes/', views.admin_reportes, name='admin_reportes'),
    
    # Admin - Períodos Académicos
    path('admin/periodos/', views.admin_periodos, name='admin_periodos'),
    path('admin/periodos/crear/', views.admin_crear_periodo, name='admin_crear_periodo'),
    path('admin/periodos/editar/<int:periodo_id>/', views.admin_editar_periodo, name='admin_editar_periodo'),
    path('admin/periodos/eliminar/<int:periodo_id>/', views.admin_eliminar_periodo, name='admin_eliminar_periodo'),
    
    # Admin - Grupos
    path('admin/grupos/', views.admin_grupos, name='admin_grupos'),
    path('admin/grupos/crear/', views.admin_crear_grupo, name='admin_crear_grupo'),
    path('admin/grupos/editar/<int:grupo_id>/', views.admin_editar_grupo, name='admin_editar_grupo'),
    path('admin/grupos/eliminar/<int:grupo_id>/', views.admin_eliminar_grupo, name='admin_eliminar_grupo'),
    
    # Admin - Materias
    path('admin/materias/', views.admin_materias, name='admin_materias'),
    path('admin/materias/crear/', views.admin_crear_materia, name='admin_crear_materia'),
    path('admin/materias/editar/<int:materia_id>/', views.admin_editar_materia, name='admin_editar_materia'),
    path('admin/materias/eliminar/<int:materia_id>/', views.admin_eliminar_materia, name='admin_eliminar_materia'),

    # Admin - Historial y Asignaciones
    path('admin/historial/', views.admin_historial, name='admin_historial'),
    path('admin/asignar-estudiantes/', views.admin_asignar_estudiantes, name='admin_asignar_estudiantes'),
    path('admin/asignar-profesor/', views.admin_asignar_profesor, name='admin_asignar_profesor'),
    
    # Profesor
    path('profesor/', views.profesor_dashboard, name='profesor_dashboard'),
    path('profesor/notas/', views.profesor_ingresar_notas, name='profesor_ingresar_notas'),
    path('profesor/guardar-notas/', views.profesor_guardar_notas, name='profesor_guardar_notas'),
    path('profesor/asignar-estudiantes/', views.profesor_asignar_estudiantes, name='profesor_asignar_estudiantes'),
    
    # Estudiante
    path('estudiante/', views.estudiante_dashboard, name='estudiante_dashboard'),
    path('estudiante/seleccionar-materia/', views.estudiante_seleccionar_materia, name='estudiante_seleccionar_materia'),
    path('estudiante/notas/', views.estudiante_ver_notas, name='estudiante_ver_notas'),
    path('estudiante/notas/<int:materia_grupo_id>/', views.estudiante_ver_notas, name='estudiante_ver_notas_materia'),
]
