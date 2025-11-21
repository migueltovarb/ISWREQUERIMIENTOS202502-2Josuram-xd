os.environ.setdefault('DJANGO_SETTINGS_MODULE','SGEN.settings'
django.setup() 
from sgenapp.models import Usuario,PeriodoAcademico,Grupo,Materia,MateriaGrupo,EstudianteGrupo,TipoEvaluacion,Calificacion 
print('usuarios',Usuario.objects.count()) 
print('periodos',PeriodoAcademico.objects.count()) 
print('grupos',Grupo.objects.count()) 
print('materias',Materia.objects.count()) 
print('materia_grupo',MateriaGrupo.objects.count()) 
print('estudiante_grupo',EstudianteGrupo.objects.count()) 
print('tipos',TipoEvaluacion.objects.count()) 
