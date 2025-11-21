"""
Script para crear datos de prueba en SGEN
Ejecutar: cd C:\Users\USUARIO\Desktop\Final\SGEN
Ejecutar: python manage.py shell < crear_datos_prueba.py
"""

from sgenapp.models import (
    Usuario, Admin, Profesor, Estudiante, PeriodoAcademico, 
    Grupo, Materia, MateriaGrupo, EstudianteGrupo, TipoEvaluacion, Calificacion
)
from datetime import date, timedelta

# Eliminar datos anteriores (opcional)
# Usuario.objects.all().delete()

print("=== Creando Períodos Académicos ===")
periodo1, created = PeriodoAcademico.objects.get_or_create(
    nombre="2025-1",
    defaults={
        "descripcion": "Primer semestre 2025",
        "activo": True,
        "fecha_inicio": date(2025, 1, 15),
        "fecha_fin": date(2025, 6, 15)
    }
)
print(f"Período 2025-1: {'Creado' if created else 'Ya existe'}")

periodo2, created = PeriodoAcademico.objects.get_or_create(
    nombre="2025-2",
    defaults={
        "descripcion": "Segundo semestre 2025",
        "activo": True,
        "fecha_inicio": date(2025, 7, 15),
        "fecha_fin": date(2025, 12, 15)
    }
)
print(f"Período 2025-2: {'Creado' if created else 'Ya existe'}")

print("\n=== Creando Grupos ===")
grupo10a, created = Grupo.objects.get_or_create(
    nombre="10A",
    periodo=periodo1
)
print(f"Grupo 10A: {'Creado' if created else 'Ya existe'}")

grupo10b, created = Grupo.objects.get_or_create(
    nombre="10B",
    periodo=periodo1
)
print(f"Grupo 10B: {'Creado' if created else 'Ya existe'}")

print("\n=== Creando Materias ===")
math, created = Materia.objects.get_or_create(
    codigo="MAT101",
    defaults={"nombre": "Matematicas I"}
)
print(f"Materia MAT101: {'Creada' if created else 'Ya existe'}")

spanish, created = Materia.objects.get_or_create(
    codigo="ESP101",
    defaults={"nombre": "Espanol"}
)
print(f"Materia ESP101: {'Creada' if created else 'Ya existe'}")

english, created = Materia.objects.get_or_create(
    codigo="ENG101",
    defaults={"nombre": "Ingles"}
)
print(f"Materia ENG101: {'Creada' if created else 'Ya existe'}")

print("\n=== Creando Tipos de Evaluación ===")
parcial1, created = TipoEvaluacion.objects.get_or_create(
    nombre="Parcial 1",
    defaults={"porcentaje": 25}
)
print(f"Evaluación Parcial 1: {'Creada' if created else 'Ya existe'}")

parcial2, created = TipoEvaluacion.objects.get_or_create(
    nombre="Parcial 2",
    defaults={"porcentaje": 25}
)
print(f"Evaluación Parcial 2: {'Creada' if created else 'Ya existe'}")

final, created = TipoEvaluacion.objects.get_or_create(
    nombre="Examen Final",
    defaults={"porcentaje": 50}
)
print(f"Evaluación Examen Final: {'Creada' if created else 'Ya existe'}")

print("\n=== Creando Usuarios ===")

# Profesor
prof_user, created = Usuario.objects.get_or_create(
    username="profesor1",
    defaults={
        "email": "profesor1@sgen.edu",
        "first_name": "Carlos",
        "documento": "1234567890",
        "rol": "2"
    }
)
if created:
    prof_user.set_password("profesor123")
    prof_user.save()
    Profesor.objects.get_or_create(usuario=prof_user)
    print("Profesor creado: profesor1")
else:
    print("Profesor profesor1: Ya existe")

# Estudiantes
for i in range(1, 6):
    est_user, created = Usuario.objects.get_or_create(
        username=f"estudiante{i}",
        defaults={
            "email": f"estudiante{i}@sgen.edu",
            "first_name": f"Estudiante {i}",
            "documento": f"000000{i}",
            "rol": "3"
        }
    )
    if created:
        est_user.set_password("estudiante123")
        est_user.save()
        est_profile, _ = Estudiante.objects.get_or_create(usuario=est_user)
        print(f"Estudiante {i} creado")
    else:
        print(f"Estudiante {i}: Ya existe")

print("\n=== Asignando Materias a Grupos ===")

# Asignar materias a grupos
MateriaGrupo.objects.get_or_create(
    materia=math, grupo=grupo10a, profesor=prof_user
)
MateriaGrupo.objects.get_or_create(
    materia=spanish, grupo=grupo10a, profesor=prof_user
)
MateriaGrupo.objects.get_or_create(
    materia=english, grupo=grupo10b, profesor=prof_user
)
print("Materias asignadas a grupos")

print("\n=== Inscribiendo Estudiantes en Grupos ===")

# Inscribir estudiantes
estudiantes = Usuario.objects.filter(rol="3")[:3]
for est in estudiantes:
    EstudianteGrupo.objects.get_or_create(
        estudiante=est, grupo=grupo10a
    )
print(f"{len(estudiantes)} estudiantes inscritos en grupo 10A")

print("\n=== Creando Calificaciones de Ejemplo ===")

# Crear algunas calificaciones de ejemplo
materias_grupos = MateriaGrupo.objects.all()[:2]
evaluaciones = [parcial1, parcial2, final]
notas = [3.5, 4.0, 4.5]

for mg in materias_grupos:
    for est_grupo in EstudianteGrupo.objects.filter(grupo=mg.grupo)[:2]:
        for eval, nota in zip(evaluaciones, notas):
            Calificacion.objects.get_or_create(
                estudiante=est_grupo.estudiante,
                materia_grupo=mg,
                tipo_evaluacion=eval,
                defaults={
                    "nota": nota,
                    "observacion": "Calificación registrada",
                    "estado": "registrada"
                }
            )

print("Calificaciones de ejemplo creadas")

print("\n" + "="*50)
print("DATOS DE PRUEBA CREADOS EXITOSAMENTE")
print("="*50)
print("\nCREDENCIALES DE PRUEBA:")
print("─" * 50)
print("PROFESOR:")
print("  Usuario: profesor1")
print("  Contraseña: profesor123")
print("\nESTUDIANTES:")
for i in range(1, 6):
    print(f"  Usuario: estudiante{i}")
    print(f"  Contraseña: estudiante123")
print("\n" + "="*50)
