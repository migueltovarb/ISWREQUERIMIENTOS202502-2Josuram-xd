"""
Script para crear las plantillas HTML necesarias para SGEN
Ejecutar: python crear_templates.py
"""

import os

TEMPLATES_PATH = "sgenapp/templates/"

# CSS Base reutilizable
CSS_BASE = """
  :root{
    --brand-blue: #1565C0;
    --brand-red: #D32F2F;
    --success: #2E7D32;
    --warning: #ED6C02;
    --bg:#FFFFFF;
    --text:#111111;
    --muted:#6B7280;
    --border:#DADCE0;
    --shadow:0 8px 24px rgba(16,24,40,.08);
    --font-sans:ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Inter, "Helvetica Neue", Arial, sans-serif;
    --space-2:.5rem;
    --space-3:.75rem;
    --space-4:1rem;
    --space-6:1.5rem;
    --space-8:2rem;
    --radius-sm:.5rem;
    --radius-xl:1.25rem;
  }
  *{box-sizing:border-box}
  html,body{height:100%; margin:0}
  body{font-family:var(--font-sans); font-size:15px; color:var(--text); background:linear-gradient(180deg,#fafafb, #f4f6fa 60%, #eef2f7)}
  .container{max-width:1200px; margin:0 auto; padding:var(--space-8)}
  .header{display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-8)}
  .header h1{margin:0}
  .header-small{display:flex; gap:var(--space-4)}
  .btn{appearance:none; border:1px solid var(--border); background:#e5e7eb; color:var(--text); padding:.5rem .75rem; border-radius:6px; font-weight:600; cursor:pointer; font-size:14px; transition:.15s}
  .btn.primary{background:var(--brand-blue); color:#fff; border:none}
  .btn.primary:hover{background:#0D47A1}
  .btn.danger{background:var(--brand-red); color:#fff; border:none}
  .btn.danger:hover{background:#B71C1C}
  .btn.success{background:var(--success); color:#fff; border:none}
  .card{background:var(--bg); border:1px solid var(--border); border-radius:var(--radius-xl); box-shadow:var(--shadow); padding:var(--space-6); margin-bottom:var(--space-6)}
  .card h2{margin:0 0 var(--space-4)}
  .nav{background:var(--bg); border-bottom:1px solid var(--border); padding:var(--space-4); margin-bottom:var(--space-8); display:flex; gap:var(--space-4); flex-wrap:wrap}
  .nav a{text-decoration:none; color:var(--brand-blue); font-weight:600; padding:.5rem 1rem; border-radius:.5rem}
  .nav a:hover{background:var(--border)}
  .table{width:100%; border-collapse:separate; border-spacing:0; border:1px solid var(--border); border-radius:var(--radius-sm); overflow:hidden}
  .table th, .table td{padding:.75rem; border-bottom:1px solid var(--border); text-align:left}
  .table thead th{background:#F7F7F9; font-weight:700}
  .table tr:last-child td{border-bottom:none}
  .form-group{margin-bottom:var(--space-4)}
  .form-group label{display:block; font-weight:600; margin-bottom:.25rem}
  .form-group input, .form-group select, .form-group textarea{width:100%; padding:.5rem; border:1px solid var(--border); border-radius:.5rem; font-family:var(--font-sans); font-size:15px}
  .form-group input:focus, .form-group select:focus, .form-group textarea:focus{outline:none; box-shadow:0 0 0 3px rgba(21,101,192,.18); border-color:var(--brand-blue)}
  .message{padding:var(--space-3) var(--space-4); border-radius:.5rem; margin-bottom:var(--space-4); border-left:4px solid}
  .message.success{background:rgba(46,125,50,.06); border-color:var(--success); color:var(--success)}
  .message.error{background:rgba(198,40,40,.06); border-color:var(--brand-red); color:var(--brand-red)}
  .message.warning{background:rgba(237,108,2,.06); border-color:var(--warning); color:var(--warning)}
"""

templates = {
    "admin_usuarios.html": """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Gestionar Usuarios • SGEN</title>
<style>
""" + CSS_BASE + """
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Gestionar Usuarios</h1>
      <form method="POST" action="{% url 'logout' %}" style="display:inline">
        {% csrf_token %}
        <button type="submit" class="btn danger">Cerrar sesión</button>
      </form>
    </div>

    <div class="nav">
      <a href="{% url 'admin_usuarios' %}">Usuarios</a>
      <a href="{% url 'admin_reportes' %}">Reportes</a>
      <a href="{% url 'admin_dashboard' %}">Inicio</a>
    </div>

    <div class="card">
      <h1>Usuarios del Sistema</h1>
      <a href="{% url 'admin_crear_usuario' %}" class="btn primary">+ Crear Usuario</a>
    </div>

    <div class="card">
      <h2>Administradores</h2>
      {% if admins %}
        <table class="table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Documento</th>
              <th>Correo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {% for admin in admins %}
            <tr>
              <td>{{ admin.first_name }}</td>
              <td>{{ admin.documento }}</td>
              <td>{{ admin.email }}</td>
              <td style="display:flex; gap:.5rem">
                <a href="{% url 'admin_editar_usuario' admin.id_usuario %}" class="btn primary">Editar</a>
                <a href="{% url 'admin_eliminar_usuario' admin.id_usuario %}" class="btn danger" onclick="return confirm('¿Estás seguro?')">Eliminar</a>
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      {% else %}
        <p>No hay administradores registrados</p>
      {% endif %}
    </div>

    <div class="card">
      <h2>Profesores</h2>
      {% if profesores %}
        <table class="table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Documento</th>
              <th>Correo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {% for profesor in profesores %}
            <tr>
              <td>{{ profesor.first_name }}</td>
              <td>{{ profesor.documento }}</td>
              <td>{{ profesor.email }}</td>
              <td style="display:flex; gap:.5rem">
                <a href="{% url 'admin_editar_usuario' profesor.id_usuario %}" class="btn primary">Editar</a>
                <a href="{% url 'admin_eliminar_usuario' profesor.id_usuario %}" class="btn danger" onclick="return confirm('¿Estás seguro?')">Eliminar</a>
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      {% else %}
        <p>No hay profesores registrados</p>
      {% endif %}
    </div>

    <div class="card">
      <h2>Estudiantes</h2>
      {% if estudiantes %}
        <table class="table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Documento</th>
              <th>Correo</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {% for estudiante in estudiantes %}
            <tr>
              <td>{{ estudiante.first_name }}</td>
              <td>{{ estudiante.documento }}</td>
              <td>{{ estudiante.email }}</td>
              <td style="display:flex; gap:.5rem">
                <a href="{% url 'admin_editar_usuario' estudiante.id_usuario %}" class="btn primary">Editar</a>
                <a href="{% url 'admin_eliminar_usuario' estudiante.id_usuario %}" class="btn danger" onclick="return confirm('¿Estás seguro?')">Eliminar</a>
              </td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      {% else %}
        <p>No hay estudiantes registrados</p>
      {% endif %}
    </div>
  </div>
</body>
</html>""",

    "admin_crear_usuario.html": """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Crear Usuario • SGEN</title>
<style>
""" + CSS_BASE + """
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Crear Nuevo Usuario</h1>
    </div>

    <div class="card">
      <form method="POST">
        {% csrf_token %}
        
        <div class="form-group">
          <label for="nombre">Nombre Completo</label>
          <input type="text" id="nombre" name="nombre" required />
        </div>

        <div class="form-group">
          <label for="documento">Documento</label>
          <input type="text" id="documento" name="documento" required />
        </div>

        <div class="form-group">
          <label for="correo">Correo</label>
          <input type="email" id="correo" name="correo" required />
        </div>

        <div class="form-group">
          <label for="rol">Tipo de Usuario</label>
          <select id="rol" name="rol" required>
            <option value="">Seleccionar...</option>
            {% for value, label in roles %}
            <option value="{{ value }}">{{ label }}</option>
            {% endfor %}
          </select>
        </div>

        <div class="form-group">
          <label for="contraseña">Contraseña</label>
          <input type="password" id="contraseña" name="contraseña" required />
        </div>

        <div style="display:flex; gap:var(--space-3)">
          <button type="submit" class="btn primary">Crear Usuario</button>
          <a href="{% url 'admin_usuarios' %}" class="btn">Cancelar</a>
        </div>
      </form>
    </div>
  </div>
</body>
</html>""",

    "admin_editar_usuario.html": """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Editar Usuario • SGEN</title>
<style>
""" + CSS_BASE + """
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Editar Usuario</h1>
    </div>

    <div class="card">
      <form method="POST">
        {% csrf_token %}
        
        <div class="form-group">
          <label for="nombre">Nombre Completo</label>
          <input type="text" id="nombre" name="nombre" value="{{ usuario.first_name }}" required />
        </div>

        <div class="form-group">
          <label>Documento</label>
          <input type="text" value="{{ usuario.documento }}" disabled />
        </div>

        <div class="form-group">
          <label for="correo">Correo</label>
          <input type="email" id="correo" name="correo" value="{{ usuario.email }}" required />
        </div>

        <div class="form-group">
          <label for="rol">Tipo de Usuario</label>
          <select id="rol" name="rol" required>
            {% for value, label in roles %}
            <option value="{{ value }}" {% if usuario.rol == value %}selected{% endif %}>{{ label }}</option>
            {% endfor %}
          </select>
        </div>

        <div style="display:flex; gap:var(--space-3)">
          <button type="submit" class="btn primary">Guardar Cambios</button>
          <a href="{% url 'admin_usuarios' %}" class="btn">Cancelar</a>
        </div>
      </form>
    </div>
  </div>
</body>
</html>""",

    "admin_reportes.html": """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Reportes • SGEN</title>
<style>
""" + CSS_BASE + """
</style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Reportes del Sistema</h1>
    </div>

    <div class="nav">
      <a href="{% url 'admin_usuarios' %}">Usuarios</a>
      <a href="{% url 'admin_reportes' %}">Reportes</a>
      <a href="{% url 'admin_dashboard' %}">Inicio</a>
    </div>

    <div class="card">
      <h2>Filtrar Reportes</h2>
      <form method="GET" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:var(--space-4)">
        <div class="form-group">
          <label for="periodo">Período</label>
          <select name="periodo" id="periodo">
            <option value="">Todos</option>
            {% for periodo in periodos %}
            <option value="{{ periodo.id }}" {% if filtro_periodo == periodo.id|stringformat:"s" %}selected{% endif %}>{{ periodo.nombre }}</option>
            {% endfor %}
          </select>
        </div>

        <div class="form-group">
          <label for="grupo">Grupo</label>
          <select name="grupo" id="grupo">
            <option value="">Todos</option>
            {% for grupo in grupos %}
            <option value="{{ grupo.id }}" {% if filtro_grupo == grupo.id|stringformat:"s" %}selected{% endif %}>{{ grupo.nombre }}</option>
            {% endfor %}
          </select>
        </div>

        <div class="form-group">
          <label for="materia">Materia</label>
          <select name="materia" id="materia">
            <option value="">Todas</option>
            {% for materia in materias %}
            <option value="{{ materia.id }}" {% if filtro_materia == materia.id|stringformat:"s" %}selected{% endif %}>{{ materia.nombre }}</option>
            {% endfor %}
          </select>
        </div>

        <div style="display:flex; align-items:flex-end">
          <button type="submit" class="btn primary">Filtrar</button>
        </div>
      </form>
    </div>

    <div class="card">
      <h2>Resultados</h2>
      {% if reportes %}
        <table class="table">
          <thead>
            <tr>
              <th>Estudiante</th>
              <th>Materia</th>
              <th>Evaluación</th>
              <th>Nota</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {% for reporte in reportes %}
            <tr>
              <td>{{ reporte.estudiante.first_name }}</td>
              <td>{{ reporte.materia_grupo.materia.nombre }}</td>
              <td>{{ reporte.tipo_evaluacion.nombre }}</td>
              <td>{{ reporte.nota|default:"Pendiente" }}</td>
              <td>{{ reporte.get_estado_display }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      {% else %}
        <p>No hay reportes para los filtros seleccionados</p>
      {% endif %}
    </div>
  </div>
</body>
</html>""",
}

def crear_templates():
    """Crear todos los templates"""
    os.makedirs(TEMPLATES_PATH, exist_ok=True)
    
    for nombre, contenido in templates.items():
        ruta = os.path.join(TEMPLATES_PATH, nombre)
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"✓ Creado: {ruta}")

if __name__ == "__main__":
    crear_templates()
    print("\nTodos los templates han sido creados exitosamente")
