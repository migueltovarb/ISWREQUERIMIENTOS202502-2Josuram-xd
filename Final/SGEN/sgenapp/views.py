from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q, Avg
from .models import (
    Usuario, Admin, Profesor, Estudiante, Materia, Grupo, MateriaGrupo,
    EstudianteGrupo, TipoEvaluacion, Calificacion, PeriodoAcademico, HistorialAcciones
)

# ============ AUTENTICACIÓN ============

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vista de inicio de sesión"""
    # Si ya está logueado, redirige según su rol
    if request.user.is_authenticated:
        if request.user.rol == '1':
            return redirect('admin_dashboard')
        elif request.user.rol == '2':
            return redirect('profesor_dashboard')
        else:
            return redirect('estudiante_dashboard')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.first_name or user.username}!')
            
            # Redirigir según el rol
            if user.rol == '1':  # Admin
                return redirect('admin_dashboard')
            elif user.rol == '2':  # Profesor
                return redirect('profesor_dashboard')
            else:  # Estudiante (3)
                return redirect('estudiante_dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'login.html')

@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')

# ============ PANEL ADMINISTRADOR ============

@login_required(login_url='login')
def admin_dashboard(request):
    """Dashboard del administrador"""
    if request.user.rol != '1':
        messages.error(request, 'No tiene permisos de administrador.')
        return redirect('login')
    
    context = {
        'total_usuarios': Usuario.objects.count(),
        'total_profesores': Usuario.objects.filter(rol='2').count(),
        'total_estudiantes': Usuario.objects.filter(rol='3').count(),
        'periodos': PeriodoAcademico.objects.all(),
    }
    return render(request, 'admin_dashboard.html', context)

@login_required(login_url='login')
def admin_usuarios(request):
    """Gestión de usuarios para admin"""
    if request.user.rol != '1':
        return redirect('login')
    
    admins = Usuario.objects.filter(rol='1')
    profesores = Usuario.objects.filter(rol='2')
    estudiantes = Usuario.objects.filter(rol='3')
    
    context = {
        'admins': admins,
        'profesores': profesores,
        'estudiantes': estudiantes,
    }
    return render(request, 'admin_usuarios.html', context)

@login_required(login_url='login')
def admin_crear_usuario(request):
    """Crear nuevo usuario"""
    if request.user.rol != '1':
        return redirect('login')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        documento = request.POST.get('documento')
        correo = request.POST.get('correo')
        rol = request.POST.get('rol')
        contraseña = request.POST.get('contraseña')
        
        try:
            usuario = Usuario.objects.create_user(
                username=documento,
                email=correo,
                password=contraseña,
                first_name=nombre,
                documento=documento,
                rol=rol
            )
            
            # Crear perfil según rol
            if rol == '1':
                Admin.objects.create(usuario=usuario)
            elif rol == '2':
                Profesor.objects.create(usuario=usuario)
            elif rol == '3':
                Estudiante.objects.create(usuario=usuario)
            
            # Registrar en historial
            rol_nombre = {'1': 'Administrador', '2': 'Profesor', '3': 'Estudiante'}.get(rol, 'Usuario')
            HistorialAcciones.objects.create(
                usuario=request.user,
                accion='Creó usuario',
                descripcion=f"Creó {rol_nombre}: {nombre} ({documento})"
            )
            
            messages.success(request, f'Usuario {nombre} creado exitosamente.')
            return redirect('admin_usuarios')
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
    
    context = {'roles': [('1', 'Administrador'), ('2', 'Profesor'), ('3', 'Estudiante')]}
    return render(request, 'admin_crear_usuario.html', context)

@login_required(login_url='login')
def admin_editar_usuario(request, usuario_id):
    """Editar usuario"""
    if request.user.rol != '1':
        return redirect('login')
    
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    
    if request.method == 'POST':
        usuario_anterior = {
            'nombre': usuario.first_name,
            'correo': usuario.email,
            'rol': usuario.rol
        }
        
        usuario.first_name = request.POST.get('nombre')
        usuario.email = request.POST.get('correo')
        usuario.rol = request.POST.get('rol')
        usuario.save()
        
        # Registrar en historial
        cambios = []
        if usuario_anterior['nombre'] != usuario.first_name:
            cambios.append(f"Nombre: {usuario_anterior['nombre']} → {usuario.first_name}")
        if usuario_anterior['correo'] != usuario.email:
            cambios.append(f"Correo: {usuario_anterior['correo']} → {usuario.email}")
        if usuario_anterior['rol'] != usuario.rol:
            rol_map = {'1': 'Administrador', '2': 'Profesor', '3': 'Estudiante'}
            cambios.append(f"Rol: {rol_map.get(usuario_anterior['rol'])} → {rol_map.get(usuario.rol)}")
        
        HistorialAcciones.objects.create(
            usuario=request.user,
            accion='Editó usuario',
            descripcion=f"Editó {usuario.first_name}: {'; '.join(cambios)}"
        )
        
        messages.success(request, 'Usuario actualizado exitosamente.')
        return redirect('admin_usuarios')
    
    context = {
        'usuario': usuario,
        'roles': [('1', 'Administrador'), ('2', 'Profesor'), ('3', 'Estudiante')]
    }
    return render(request, 'admin_editar_usuario.html', context)

@login_required(login_url='login')
def admin_eliminar_usuario(request, usuario_id):
    """Eliminar usuario"""
    if request.user.rol != '1':
        return redirect('login')
    
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    nombre = usuario.first_name
    documento = usuario.documento
    
    # Registrar en historial antes de eliminar
    HistorialAcciones.objects.create(
        usuario=request.user,
        accion='Eliminó usuario',
        descripcion=f"Eliminó usuario: {nombre} ({documento})"
    )
    
    usuario.delete()
    messages.success(request, f'Usuario {nombre} eliminado exitosamente.')
    return redirect('admin_usuarios')

@login_required(login_url='login')
def admin_reportes(request):
    """Reportes filtrados"""
    if request.user.rol != '1':
        return redirect('login')
    
    periodo = request.GET.get('periodo')
    grupo = request.GET.get('grupo')
    materia = request.GET.get('materia')
    
    reportes = Calificacion.objects.all()
    
    if periodo:
        reportes = reportes.filter(materia_grupo__grupo__periodo_id=periodo)
    if grupo:
        reportes = reportes.filter(materia_grupo__grupo_id=grupo)
    if materia:
        reportes = reportes.filter(materia_grupo__materia_id=materia)
    
    context = {
        'reportes': reportes,
        'periodos': PeriodoAcademico.objects.all(),
        'grupos': Grupo.objects.all(),
        'materias': Materia.objects.all(),
        'filtro_periodo': periodo,
        'filtro_grupo': grupo,
        'filtro_materia': materia,
    }
    return render(request, 'admin_reportes.html', context)

# ============ PANEL PROFESOR ============

@login_required(login_url='login')
def profesor_dashboard(request):
    """Dashboard del profesor"""
    if request.user.rol != '2':
        messages.error(request, 'No tiene permisos de profesor.')
        return redirect('login')
    
    # Materias que imparte este profesor
    materias_grupos = MateriaGrupo.objects.filter(profesor=request.user)
    
    context = {
        'materias_grupos': materias_grupos,
        'total_grupos': materias_grupos.count(),
    }
    return render(request, 'profesor_dashboard.html', context)

@login_required(login_url='login')
def profesor_ingresar_notas(request):
    """Ingreso de calificaciones"""
    if request.user.rol != '2':
        return redirect('login')
    
    if request.method == 'GET':
        periodos = PeriodoAcademico.objects.filter(activo=True)
        materias_grupos = MateriaGrupo.objects.filter(profesor=request.user)
        tipos_evaluacion = TipoEvaluacion.objects.all()
        
        context = {
            'periodos': periodos,
            'materias_grupos': materias_grupos,
            'tipos_evaluacion': tipos_evaluacion,
        }
        return render(request, 'profesor_seleccionar_datos.html', context)
    
    # POST: Procesar datos y mostrar tabla de estudiantes
    materia_grupo_id = request.POST.get('materia_grupo')
    tipo_evaluacion_id = request.POST.get('tipo_evaluacion')
    
    materia_grupo = get_object_or_404(MateriaGrupo, id=materia_grupo_id, profesor=request.user)
    tipo_evaluacion = get_object_or_404(TipoEvaluacion, id=tipo_evaluacion_id)
    
    # Estudiantes en este grupo
    estudiantes_grupo = EstudianteGrupo.objects.filter(grupo=materia_grupo.grupo)
    
    context = {
        'materia_grupo': materia_grupo,
        'tipo_evaluacion': tipo_evaluacion,
        'estudiantes_grupo': estudiantes_grupo,
    }
    return render(request, 'profesor_tabla_notas.html', context)

@login_required(login_url='login')
def profesor_guardar_notas(request):
    """Guardar notas ingresadas"""
    if request.method == 'POST' and request.user.rol == '2':
        materia_grupo_id = request.POST.get('materia_grupo_id')
        tipo_evaluacion_id = request.POST.get('tipo_evaluacion_id')
        
        materia_grupo = get_object_or_404(MateriaGrupo, id=materia_grupo_id)
        tipo_evaluacion = get_object_or_404(TipoEvaluacion, id=tipo_evaluacion_id)
        
        # Procesar notas
        estudiantes_grupo = EstudianteGrupo.objects.filter(grupo=materia_grupo.grupo)
        notas_guardadas = 0
        
        for eg in estudiantes_grupo:
            nota = request.POST.get(f'nota_{eg.estudiante.id_usuario}')
            observacion = request.POST.get(f'observacion_{eg.estudiante.id_usuario}')
            
            if nota:
                try:
                    nota_float = float(nota)
                    calificacion, created = Calificacion.objects.update_or_create(
                        estudiante=eg.estudiante,
                        materia_grupo=materia_grupo,
                        tipo_evaluacion=tipo_evaluacion,
                        defaults={
                            'nota': nota_float,
                            'observacion': observacion or '',
                            'estado': 'registrada'
                        }
                    )
                    notas_guardadas += 1
                except ValueError:
                    messages.error(request, f'Nota inválida para estudiante {eg.estudiante.first_name}')
        
        # Registrar en historial
        if notas_guardadas > 0:
            HistorialAcciones.objects.create(
                usuario=request.user,
                accion='Guardó calificaciones',
                descripcion=f"Ingresó {notas_guardadas} notas de {materia_grupo.materia.codigo} ({materia_grupo.grupo.nombre}) - {tipo_evaluacion.nombre}"
            )
        
        messages.success(request, 'Notas guardadas exitosamente.')
        return redirect('profesor_dashboard')
    
    return redirect('profesor_ingresar_notas')

@login_required(login_url='login')
def profesor_asignar_estudiantes(request):
    """Permitir que el profesor asigne estudiantes a sus materias"""
    if request.user.rol != '2':
        return redirect('login')
    
    # Materias que imparte este profesor
    materias_grupos = MateriaGrupo.objects.filter(profesor=request.user).select_related('materia', 'grupo', 'grupo__periodo')
    
    materia_grupo_id = request.GET.get('materia_grupo')
    
    if materia_grupo_id:
        materia_grupo = get_object_or_404(MateriaGrupo, id=materia_grupo_id, profesor=request.user)
        
        # Estudiantes ya asignados a este grupo
        inscritos = set(EstudianteGrupo.objects.filter(grupo=materia_grupo.grupo).values_list('estudiante_id', flat=True))
        
        # Todos los estudiantes disponibles
        estudiantes = Usuario.objects.filter(rol='3')
        
        if request.method == 'POST':
            seleccionados = request.POST.getlist('estudiantes')
            seleccionados_set = set(int(s) for s in seleccionados) if seleccionados else set()
            
            # Remover estudiantes no seleccionados
            EstudianteGrupo.objects.filter(grupo=materia_grupo.grupo).exclude(estudiante_id__in=seleccionados_set).delete()
            
            # Agregar estudiantes nuevos
            nuevos_count = 0
            for est_id in seleccionados_set:
                if est_id not in inscritos:
                    estudiante = get_object_or_404(Usuario, id_usuario=est_id, rol='3')
                    EstudianteGrupo.objects.create(estudiante=estudiante, grupo=materia_grupo.grupo)
                    nuevos_count += 1
            
            # Registrar en historial
            HistorialAcciones.objects.create(
                usuario=request.user,
                accion='Asigno estudiantes a materia',
                descripcion=f'{materia_grupo.materia.codigo} ({materia_grupo.grupo.nombre}) - {len(seleccionados_set)} estudiantes'
            )
            
            messages.success(request, 'Estudiantes asignados correctamente.')
            return redirect('profesor_asignar_estudiantes')
        
        context = {
            'materias_grupos': materias_grupos,
            'materia_grupo': materia_grupo,
            'estudiantes': estudiantes,
            'inscritos': inscritos,
        }
        return render(request, 'profesor_asignar_estudiantes.html', context)
    
    # Sin materia_grupo seleccionada, mostrar lista
    context = {'materias_grupos': materias_grupos, 'materia_grupo': None}
    return render(request, 'profesor_asignar_estudiantes.html', context)

# ============ PANEL ESTUDIANTE ============

@login_required(login_url='login')
def estudiante_dashboard(request):
    """Dashboard del estudiante"""
    if request.user.rol != '3':
        messages.error(request, 'No tiene permisos de estudiante.')
        return redirect('login')
    
    # Grupos en los que está inscrito
    grupos = EstudianteGrupo.objects.filter(estudiante=request.user).values_list('grupo', flat=True)
    materias_disponibles = MateriaGrupo.objects.filter(grupo_id__in=grupos).distinct()
    
    context = {
        'materias_disponibles': materias_disponibles,
    }
    return render(request, 'estudiante_dashboard.html', context)

@login_required(login_url='login')
def estudiante_seleccionar_materia(request):
    """Seleccionar materia para ver notas"""
    if request.user.rol != '3':
        return redirect('login')
    
    # Materias disponibles para este estudiante
    grupos = EstudianteGrupo.objects.filter(estudiante=request.user).values_list('grupo', flat=True)
    materias = MateriaGrupo.objects.filter(grupo_id__in=grupos).distinct()
    
    context = {
        'materias': materias,
    }
    return render(request, 'estudiante_seleccionar_materia.html', context)

@login_required(login_url='login')
def estudiante_ver_notas(request, materia_grupo_id=None):
    """Ver notas del estudiante por materia"""
    if request.user.rol != '3':
        return redirect('login')
    
    if not materia_grupo_id:
        # Ver todas las notas
        grupos = EstudianteGrupo.objects.filter(estudiante=request.user).values_list('grupo', flat=True)
        calificaciones = Calificacion.objects.filter(
            estudiante=request.user,
            materia_grupo__grupo_id__in=grupos
        ).select_related('materia_grupo__materia', 'tipo_evaluacion')
        
        # Agrupar por materia
        materias_dict = {}
        for cal in calificaciones:
            materia_codigo = cal.materia_grupo.materia.codigo
            if materia_codigo not in materias_dict:
                materias_dict[materia_codigo] = {
                    'materia': cal.materia_grupo.materia,
                    'calificaciones': [],
                    'promedio': 0
                }
            materias_dict[materia_codigo]['calificaciones'].append(cal)
        
        # Calcular promedios
        for materia_codigo, data in materias_dict.items():
            calificaciones = data['calificaciones']
            if calificaciones:
                # Promedio ponderado
                suma_ponderada = sum(cal.nota * (cal.tipo_evaluacion.porcentaje / 100) 
                                    for cal in calificaciones if cal.nota)
                data['promedio'] = round(suma_ponderada, 2)
        
        context = {
            'todas_notas': True,
            'materias': list(materias_dict.values()),
        }
    else:
        # Ver notas de una materia específica
        materia_grupo = get_object_or_404(MateriaGrupo, id=materia_grupo_id)
        calificaciones = Calificacion.objects.filter(
            estudiante=request.user,
            materia_grupo=materia_grupo
        ).select_related('tipo_evaluacion')
        
        # Calcular promedio ponderado
        promedio = 0
        if calificaciones.exists():
            suma_ponderada = sum(cal.nota * (cal.tipo_evaluacion.porcentaje / 100) 
                                for cal in calificaciones if cal.nota)
            promedio = round(suma_ponderada, 2)
        
        context = {
            'todas_notas': False,
            'materia_grupo': materia_grupo,
            'calificaciones': calificaciones,
            'promedio': promedio,
        }
    
    return render(request, 'estudiante_ver_notas.html', context)


# ============ GESTIÓN DE PERÍODOS ACADÉMICOS ============

@login_required(login_url='login')
def admin_periodos(request):
    """Lista de períodos académicos"""
    if request.user.rol != '1':
        return redirect('login')
    
    periodos = PeriodoAcademico.objects.all().order_by('-fecha_inicio')
    context = {'periodos': periodos}
    return render(request, 'admin_periodos.html', context)

@login_required(login_url='login')
def admin_crear_periodo(request):
    """Crear período académico"""
    if request.user.rol != '1':
        return redirect('login')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        activo = request.POST.get('activo') == 'on'
        
        try:
            periodo = PeriodoAcademico.objects.create(
                nombre=nombre,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                activo=activo
            )
            
            HistorialAcciones.objects.create(
                usuario=request.user,
                accion='Creó período académico',
                descripcion=f"Período: {nombre} ({fecha_inicio} - {fecha_fin})"
            )
            
            messages.success(request, f'Período {nombre} creado exitosamente.')
            return redirect('admin_periodos')
        except Exception as e:
            messages.error(request, f'Error al crear período: {str(e)}')
    
    return render(request, 'admin_crear_periodo.html')

@login_required(login_url='login')
def admin_editar_periodo(request, periodo_id):
    """Editar período académico"""
    if request.user.rol != '1':
        return redirect('login')
    
    periodo = get_object_or_404(PeriodoAcademico, id=periodo_id)
    
    if request.method == 'POST':
        periodo_anterior = {
            'nombre': periodo.nombre,
            'fecha_inicio': str(periodo.fecha_inicio),
            'fecha_fin': str(periodo.fecha_fin),
            'activo': periodo.activo
        }
        
        periodo.nombre = request.POST.get('nombre')
        periodo.fecha_inicio = request.POST.get('fecha_inicio')
        periodo.fecha_fin = request.POST.get('fecha_fin')
        periodo.activo = request.POST.get('activo') == 'on'
        periodo.save()
        
        cambios = []
        if periodo_anterior['nombre'] != periodo.nombre:
            cambios.append(f"Nombre: {periodo_anterior['nombre']} → {periodo.nombre}")
        if periodo_anterior['activo'] != periodo.activo:
            cambios.append(f"Estado: {'Inactivo' if periodo_anterior['activo'] else 'Activo'} → {'Activo' if periodo.activo else 'Inactivo'}")
        
        HistorialAcciones.objects.create(
            usuario=request.user,
            accion='Editó período académico',
            descripcion=f"Editó {periodo.nombre}: {'; '.join(cambios)}"
        )
        
        messages.success(request, 'Período actualizado exitosamente.')
        return redirect('admin_periodos')
    
    context = {'periodo': periodo}
    return render(request, 'admin_editar_periodo.html', context)

@login_required(login_url='login')
def admin_eliminar_periodo(request, periodo_id):
    """Eliminar período académico"""
    if request.user.rol != '1':
        return redirect('login')
    
    periodo = get_object_or_404(PeriodoAcademico, id=periodo_id)
    nombre = periodo.nombre
    
    HistorialAcciones.objects.create(
        usuario=request.user,
        accion='Eliminó período académico',
        descripcion=f"Período: {nombre}"
    )
    
    periodo.delete()
    messages.success(request, f'Período {nombre} eliminado exitosamente.')
    return redirect('admin_periodos')


# ============ GESTIÓN DE GRUPOS ============

@login_required(login_url='login')
def admin_grupos(request):
    """Lista de grupos"""
    if request.user.rol != '1':
        return redirect('login')
    
    grupos = Grupo.objects.all().select_related('periodo').order_by('periodo', 'nombre')
    context = {'grupos': grupos}
    return render(request, 'admin_grupos.html', context)

@login_required(login_url='login')
def admin_crear_grupo(request):
    """Crear grupo"""
    if request.user.rol != '1':
        return redirect('login')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        periodo_id = request.POST.get('periodo')
        capacidad = request.POST.get('capacidad')
        
        try:
            periodo = get_object_or_404(PeriodoAcademico, id=periodo_id)
            grupo = Grupo.objects.create(
                nombre=nombre,
                periodo=periodo,
                capacidad=int(capacidad)
            )
            
            HistorialAcciones.objects.create(
                usuario=request.user,
                accion='Creó grupo',
                descripcion=f"Grupo: {nombre} - Período {periodo.nombre}"
            )
            
            messages.success(request, f'Grupo {nombre} creado exitosamente.')
            return redirect('admin_grupos')
        except Exception as e:
            messages.error(request, f'Error al crear grupo: {str(e)}')
    
    context = {'periodos': PeriodoAcademico.objects.all()}
    return render(request, 'admin_crear_grupo.html', context)

@login_required(login_url='login')
def admin_editar_grupo(request, grupo_id):
    """Editar grupo"""
    if request.user.rol != '1':
        return redirect('login')
    
    grupo = get_object_or_404(Grupo, id=grupo_id)
    
    if request.method == 'POST':
        grupo_anterior = {
            'nombre': grupo.nombre,
            'capacidad': grupo.capacidad
        }
        
        grupo.nombre = request.POST.get('nombre')
        grupo.capacidad = int(request.POST.get('capacidad'))
        grupo.save()
        
        cambios = []
        if grupo_anterior['nombre'] != grupo.nombre:
            cambios.append(f"Nombre: {grupo_anterior['nombre']} → {grupo.nombre}")
        if grupo_anterior['capacidad'] != grupo.capacidad:
            cambios.append(f"Capacidad: {grupo_anterior['capacidad']} → {grupo.capacidad}")
        
        HistorialAcciones.objects.create(
            usuario=request.user,
            accion='Editó grupo',
            descripcion=f"Editó {grupo.nombre}: {'; '.join(cambios)}"
        )
        
        messages.success(request, 'Grupo actualizado exitosamente.')
        return redirect('admin_grupos')
    
    context = {
        'grupo': grupo,
        'periodos': PeriodoAcademico.objects.all()
    }
    return render(request, 'admin_editar_grupo.html', context)

@login_required(login_url='login')
def admin_eliminar_grupo(request, grupo_id):
    """Eliminar grupo"""
    if request.user.rol != '1':
        return redirect('login')
    
    grupo = get_object_or_404(Grupo, id=grupo_id)
    nombre = grupo.nombre
    
    HistorialAcciones.objects.create(
        usuario=request.user,
        accion='Eliminó grupo',
        descripcion=f"Grupo: {nombre}"
    )
    
    grupo.delete()
    messages.success(request, f'Grupo {nombre} eliminado exitosamente.')
    return redirect('admin_grupos')


# ============ GESTIÓN DE MATERIAS ============

@login_required(login_url='login')
def admin_materias(request):
    """Lista de materias"""
    if request.user.rol != '1':
        return redirect('login')
    
    materias = Materia.objects.all().order_by('codigo')
    context = {'materias': materias}
    return render(request, 'admin_materias.html', context)

@login_required(login_url='login')
def admin_crear_materia(request):
    """Crear materia"""
    if request.user.rol != '1':
        return redirect('login')
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        creditos = request.POST.get('creditos')
        
        try:
            materia = Materia.objects.create(
                codigo=codigo,
                nombre=nombre,
                descripcion=descripcion,
                creditos=int(creditos)
            )
            
            HistorialAcciones.objects.create(
                usuario=request.user,
                accion='Creó materia',
                descripcion=f"Materia: {nombre} ({codigo})"
            )
            
            messages.success(request, f'Materia {nombre} creada exitosamente.')
            return redirect('admin_materias')
        except Exception as e:
            messages.error(request, f'Error al crear materia: {str(e)}')
    
    return render(request, 'admin_crear_materia.html')

@login_required(login_url='login')
def admin_editar_materia(request, materia_id):
    """Editar materia"""
    if request.user.rol != '1':
        return redirect('login')
    
    materia = get_object_or_404(Materia, id=materia_id)
    
    if request.method == 'POST':
        materia_anterior = {
            'nombre': materia.nombre,
            'creditos': materia.creditos
        }
        
        materia.nombre = request.POST.get('nombre')
        materia.descripcion = request.POST.get('descripcion')
        materia.creditos = int(request.POST.get('creditos'))
        materia.save()
        
        cambios = []
        if materia_anterior['nombre'] != materia.nombre:
            cambios.append(f"Nombre: {materia_anterior['nombre']} → {materia.nombre}")
        if materia_anterior['creditos'] != materia.creditos:
            cambios.append(f"Créditos: {materia_anterior['creditos']} → {materia.creditos}")
        
        HistorialAcciones.objects.create(
            usuario=request.user,
            accion='Editó materia',
            descripcion=f"Editó {materia.nombre} ({materia.codigo}): {'; '.join(cambios) if cambios else 'Descripción'}"
        )
        
        messages.success(request, 'Materia actualizada exitosamente.')
        return redirect('admin_materias')
    
    context = {'materia': materia}
    return render(request, 'admin_editar_materia.html', context)

@login_required(login_url='login')
def admin_eliminar_materia(request, materia_id):
    """Eliminar materia"""
    if request.user.rol != '1':
        return redirect('login')
    
    materia = get_object_or_404(Materia, id=materia_id)
    nombre = materia.nombre
    codigo = materia.codigo
    
    HistorialAcciones.objects.create(
        usuario=request.user,
        accion='Eliminó materia',
        descripcion=f"Materia: {nombre} ({codigo})"
    )
    
    materia.delete()
    messages.success(request, f'Materia {nombre} eliminada exitosamente.')
    return redirect('admin_materias')


# ============ HISTORIAL DE ACCIONES ============


@login_required(login_url='login')
def admin_historial(request):
    """Ver historial de acciones (auditoría)"""
    if request.user.rol != '1':
        return redirect('login')

    q = request.GET.get('q')
    acciones = HistorialAcciones.objects.select_related('usuario').all()
    if q:
        acciones = acciones.filter(
            Q(accion__icontains=q) | Q(descripcion__icontains=q) | Q(usuario__username__icontains=q)
        )

    context = {'acciones': acciones.order_by('-fecha_hora'), 'query': q}
    return render(request, 'admin_historial.html', context)


# ============ ASIGNACIONES (ADMIN) ============


@login_required(login_url='login')
def admin_asignar_estudiantes(request):
    """Asignar/Remover estudiantes a un grupo (admin)"""
    if request.user.rol != '1':
        return redirect('login')

    grupo_id = request.GET.get('grupo')
    grupos = Grupo.objects.select_related('periodo').all()
    estudiantes = Usuario.objects.filter(rol='3')

    if grupo_id:
        grupo = get_object_or_404(Grupo, id=grupo_id)
        inscritos = set(EstudianteGrupo.objects.filter(grupo=grupo).values_list('estudiante_id', flat=True))
        if request.method == 'POST':
            seleccionados = request.POST.getlist('estudiantes')
            seleccionados_set = set(int(s) for s in seleccionados)

            # Eliminar los que ya no están seleccionados
            EstudianteGrupo.objects.filter(grupo=grupo).exclude(estudiante_id__in=seleccionados_set).delete()

            # Añadir los nuevos
            for est_id in seleccionados_set:
                if est_id not in inscritos:
                    estudiante = get_object_or_404(Usuario, id_usuario=est_id, rol='3')
                    EstudianteGrupo.objects.create(estudiante=estudiante, grupo=grupo)

            HistorialAcciones.objects.create(
                usuario=request.user,
                accion='Asignó estudiantes a grupo',
                descripcion=f'Grupo: {grupo.nombre} - {grupo.periodo.nombre} (Asignados: {len(seleccionados_set)})'
            )
            messages.success(request, 'Asignaciones actualizadas correctamente.')
            return redirect('admin_asignar_estudiantes')

        context = {'grupos': grupos, 'grupo': grupo, 'estudiantes': estudiantes, 'inscritos': inscritos}
        return render(request, 'admin_asignar_estudiantes.html', context)
    
    # Si no hay grupo seleccionado, mostrar lista de grupos
    context = {'grupos': grupos, 'grupo': None, 'estudiantes': estudiantes}
    return render(request, 'admin_asignar_estudiantes.html', context)


@login_required(login_url='login')
def admin_asignar_profesor(request):
    """Asignar un profesor a una materia dentro de un grupo (admin)"""
    if request.user.rol != '1':
        return redirect('login')

    if request.method == 'POST':
        materia_id = request.POST.get('materia')
        grupo_id = request.POST.get('grupo')
        profesor_id = request.POST.get('profesor')

        try:
            materia = get_object_or_404(Materia, id=materia_id)
            grupo = get_object_or_404(Grupo, id=grupo_id)
            profesor = get_object_or_404(Usuario, id_usuario=profesor_id, rol='2')

            mg, created = MateriaGrupo.objects.get_or_create(materia=materia, grupo=grupo, defaults={'profesor': profesor})
            if not created:
                mg.profesor = profesor
                mg.save()

            HistorialAcciones.objects.create(
                usuario=request.user,
                accion='Asignó profesor a materia',
                descripcion=f'Profesor {profesor.username} asignado a {materia.codigo} - {grupo.nombre} ({grupo.periodo.nombre})'
            )

            messages.success(request, 'Profesor asignado correctamente.')
            return redirect('admin_asignar_profesor')
        except Exception as e:
            messages.error(request, f'Error al asignar profesor: {str(e)}')

    materias = Materia.objects.all().order_by('codigo')
    grupos = Grupo.objects.select_related('periodo').all().order_by('periodo', 'nombre')
    profesores = Usuario.objects.filter(rol='2')

    context = {'materias': materias, 'grupos': grupos, 'profesores': profesores}
    return render(request, 'admin_asignar_profesor.html', context)


@login_required(login_url='login')
def admin_asignar_profesor(request):
    """Asignar profesor a una materia en un grupo (crea MateriaGrupo)"""
    if request.user.rol != '1':
        return redirect('login')

    if request.method == 'POST':
        materia_id = request.POST.get('materia')
        grupo_id = request.POST.get('grupo')
        profesor_id = request.POST.get('profesor')

        try:
            materia = get_object_or_404(Materia, id=materia_id)
            grupo = get_object_or_404(Grupo, id=grupo_id)
            profesor = get_object_or_404(Usuario, id_usuario=profesor_id, rol='2')

            mg, created = MateriaGrupo.objects.get_or_create(materia=materia, grupo=grupo, defaults={'profesor': profesor})
            if not created:
                mg.profesor = profesor
                mg.save()

            HistorialAcciones.objects.create(
                usuario=request.user,
                accion='Asignó profesor a materia',
                descripcion=f'Profesor {profesor.username} -> {materia.codigo} en {grupo.nombre}'
            )
            messages.success(request, 'Profesor asignado correctamente.')
            return redirect('admin_asignar_profesor')
        except Exception as e:
            messages.error(request, f'Error al asignar profesor: {str(e)}')

    context = {
        'materias': Materia.objects.all(),
        'grupos': Grupo.objects.select_related('periodo').all(),
        'profesores': Usuario.objects.filter(rol='2')
    }
    return render(request, 'admin_asignar_profesor.html', context)
