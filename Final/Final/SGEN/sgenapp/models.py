from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    """Clase base para todos los usuarios del sistema"""
    ROLES = [
        ('1', 'Administrador'),
        ('2', 'Profesor'),
        ('3', 'Estudiante'),
    ]
    
    id_usuario = models.AutoField(primary_key=True)
    documento = models.CharField(max_length=20, unique=True)
    rol = models.CharField(max_length=1, choices=ROLES, default='3')
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"


class Admin(models.Model):
    """Administrador con privilegios especiales"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='admin_profile')
    puede_gestionar_usuarios = models.BooleanField(default=True)
    puede_gestionar_cursos = models.BooleanField(default=True)
    puede_ver_reportes = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'
    
    def __str__(self):
        return f"Admin: {self.usuario.username}"


class Profesor(models.Model):
    """Profesor con permisos para gestionar sus cursos"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='profesor_profile')
    numero_empleado = models.CharField(max_length=20, unique=True, null=True, blank=True)
    puede_crear_cursos = models.BooleanField(default=True)
    puede_ingresar_calificaciones = models.BooleanField(default=True)
    puede_ver_estudiantes = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'
    
    def __str__(self):
        return f"Profesor: {self.usuario.username}"


class Estudiante(models.Model):
    """Estudiante con permisos limitados"""
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='estudiante_profile')
    numero_matricula = models.CharField(max_length=20, unique=True, null=True, blank=True)
    puede_ver_calificaciones = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
    
    def __str__(self):
        return f"Estudiante: {self.usuario.username}"


class PeriodoAcademico(models.Model):
    """Períodos académicos (semestres)"""
    nombre = models.CharField(max_length=50, unique=True)  # Ej: "2025-1", "2025-2"
    descripcion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    class Meta:
        verbose_name = 'Período Académico'
        verbose_name_plural = 'Períodos Académicos'
        ordering = ['-nombre']
    
    def __str__(self):
        return self.nombre


class Grupo(models.Model):
    """Grupos/Cursos"""
    nombre = models.CharField(max_length=100)  # Ej: "10A", "11B"
    periodo = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE, related_name='grupos')
    capacidad = models.PositiveIntegerField(default=30)
    
    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        unique_together = ('nombre', 'periodo')
    
    def __str__(self):
        return f"{self.nombre} - {self.periodo}"


class Materia(models.Model):
    """Asignaturas/Materias"""
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True)
    creditos = models.PositiveIntegerField(default=3)
    
    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class MateriaGrupo(models.Model):
    """Relación entre Materia, Grupo y Profesor"""
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    profesor = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, limit_choices_to={'rol': '2'})
    
    class Meta:
        verbose_name = 'Materia-Grupo'
        verbose_name_plural = 'Materias-Grupos'
        unique_together = ('materia', 'grupo')
    
    def __str__(self):
        return f"{self.materia.codigo} - {self.grupo.nombre}"


class EstudianteGrupo(models.Model):
    """Relación entre Estudiante y Grupo (inscripción)"""
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': '3'})
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Estudiante-Grupo'
        verbose_name_plural = 'Estudiantes-Grupos'
        unique_together = ('estudiante', 'grupo')
    
    def __str__(self):
        return f"{self.estudiante.username} - {self.grupo.nombre}"


class TipoEvaluacion(models.Model):
    """Tipos de evaluación (Parcial, Examen, Quiz, etc.) con sus porcentajes"""
    nombre = models.CharField(max_length=100)  # Ej: "Parcial 1", "Examen Final", "Quiz"
    porcentaje = models.FloatField()  # Porcentaje que aporta a la nota final
    
    class Meta:
        verbose_name = 'Tipo de Evaluación'
        verbose_name_plural = 'Tipos de Evaluación'
    
    def __str__(self):
        return f"{self.nombre} ({self.porcentaje}%)"


class Calificacion(models.Model):
    """Calificaciones de estudiantes"""
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': '3'})
    materia_grupo = models.ForeignKey(MateriaGrupo, on_delete=models.CASCADE)
    tipo_evaluacion = models.ForeignKey(TipoEvaluacion, on_delete=models.CASCADE)
    nota = models.FloatField(null=True, blank=True)
    observacion = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('registrada', 'Registrada'),
            ('corregida', 'Corregida'),
        ],
        default='pendiente'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        unique_together = ('estudiante', 'materia_grupo', 'tipo_evaluacion')
    
    def __str__(self):
        return f"{self.estudiante.username} - {self.materia_grupo.materia.codigo}: {self.nota}"


class HistorialAcciones(models.Model):
    """Registro de acciones del usuario para auditoría"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='acciones')
    accion = models.CharField(max_length=200)  # "Inició sesión", "Creó usuario", etc
    descripcion = models.TextField(blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Historial de Acciones'
        verbose_name_plural = 'Historiales de Acciones'
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.accion} ({self.fecha_hora})"
