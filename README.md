# Ukidd Barber

Sistema web para la gestión de reservas de una barbería.

## Descripción

Ukidd Barber permite gestionar clientes, servicios, barberos, horarios disponibles y reservas. El sistema también permite a los clientes seleccionar un servicio, barbero, fecha y hora para realizar una reserva.

## Funcionalidades

- Gestión de clientes.
- Gestión de servicios.
- Gestión de barberos.
- Gestión de disponibilidad.
- Crear reservas.
- Modificar reservas.
- Cancelar reservas.
- Visualizar agenda de reservas.
- Consulta de horarios disponibles.
- Acceso de administración protegido con contraseña.

## Tecnologías

- Python
- Flask
- SQLite
- HTML
- CSS
- Git
- GitHub

## Historias de usuario

El proyecto contempla las siguientes historias de usuario:

- **US01 — Gestión de clientes**
- **US02 — Gestión de servicios**
- **US03 — Gestión de barberos**
- **US04 — Gestión de disponibilidad**
- **US05 — Crear reserva**
- **US06 — Modificar reserva**
- **US07 — Cancelar reserva**
- **US08 — Visualizar agenda**

## Ejecución del proyecto

Crear y activar el entorno virtual:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Instalar las dependencias:

```powershell
pip install -r requirements.txt
```

Definir la contraseña del panel de administración (obligatoria para poder ingresar):

```powershell
# Windows (PowerShell)
$env:UKIDD_ADMIN_PASSWORD = "elige-una-contraseña-segura"

# Linux / macOS
export UKIDD_ADMIN_PASSWORD="elige-una-contraseña-segura"
```

Ejecutar la aplicación:

```powershell
python app.py
```

La base de datos (`database.db`) se crea automáticamente la primera vez.

## Uso

- **Sitio público**: http://127.0.0.1:5000/ — los clientes reservan su hora desde `/reservar`.
- **Administración**: http://127.0.0.1:5000/admin/login — tras ingresar la contraseña se accede a la agenda, reservas, disponibilidad, clientes, servicios y barberos.

### Variables de entorno

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `UKIDD_ADMIN_PASSWORD` | Sí | Contraseña del panel de administración. Sin ella no es posible ingresar. |
| `UKIDD_SECRET_KEY` | No | Clave para firmar las sesiones. Si no se define, se genera una al iniciar (las sesiones se cierran al reiniciar). |
| `FLASK_DEBUG` | No | Con valor `1` activa el modo debug. No usar en producción. |

## Estructura del proyecto

```
UkiddBarber/
│
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── static/
│   ├── favicon.svg
│   ├── css/
│   │   ├── base.css        (colores y reglas comunes)
│   │   ├── estilos.css     (panel de administración)
│   │   ├── inicio.css      (página de inicio)
│   │   └── reservar.css    (reserva pública)
│   └── js/
│       └── admin.js        (confirmación al eliminar/cancelar)
│
└── templates/
    ├── inicio.html
    ├── reservar.html
    ├── login.html
    ├── mensaje.html
    ├── _menu_admin.html
    ├── clientes.html
    ├── servicios.html
    ├── barberos.html
    ├── disponibilidad.html
    ├── reservas.html
    ├── editar_cliente.html
    ├── editar_servicio.html
    ├── editar_barbero.html
    ├── editar_reserva.html
    └── agenda.html
```

## Proyecto

Ukidd Barber fue desarrollado como proyecto académico para aplicar conceptos de desarrollo de software, gestión de requisitos, historias de usuario, planificación mediante sprints y control de versiones.
