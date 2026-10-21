
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

Instalar las dependencias:
pip install flask

Ejecutar la aplicación:
python app.py

Luego acceder desde el navegador a:
http://127.0.0.1:5000/

Estructura del proyecto
UkiddBarber/
│
├── app.py
├── database.py
├── README.md
├── .gitignore
│
├── static/
│   └── css/
│       ├── estilos.css
│       ├── inicio.css
│       └── reservar.css
│
└── templates/
    ├── inicio.html
    ├── reservar.html
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

Proyecto
Ukidd Barber fue desarrollado como proyecto académico para aplicar conceptos de desarrollo de software, gestión de requisitos, historias de usuario, planificación mediante sprints y control de versiones.

### 3. Guarda el cambio

Arriba a la derecha tienes el botón verde que empieza con **“Commit…”**.

Haz clic ahí.

Te aparecerá una ventana para confirmar el commit. Puedes dejar:

```text
Update README.md

y seleccionar Commit changes.
