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
- Validación de datos.
- Control de reservas duplicadas.

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
pip install -r requirements.txt

Definir la contraseña del panel de administración:
$env:UKIDD_ADMIN_PASSWORD = "elige-una-contraseña-segura"

Ejecutar la aplicación:
python app.py

La aplicación estará disponible en:
http://127.0.0.1:5000/

Uso
Sitio público
Los clientes pueden acceder al sitio público para consultar los servicios y realizar una reserva:
http://127.0.0.1:5000/

Administración
El panel administrativo está protegido mediante contraseña:
http://127.0.0.1:5000/admin/login

Desde el panel se pueden gestionar:
- Agenda
- Reservas
- Disponibilidad
- Clientes
- Servicios
- Barberos
Estructura del proyecto
UkiddBarber/
│
├── app.py
├── database.py
├── requirements.txt
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
    ├── login.html
    ├── mensaje.html
    ├── _menu_admin.html
    ├── clientes.html
    ├── servicios.html
    ├── barberos.html
    ├── disponibilidad.html
    ├── reservas.html
    ├── agenda.html
    ├── editar_cliente.html
    ├── editar_servicio.html
    ├── editar_barbero.html
    └── editar_reserva.html

Proyecto
Ukidd Barber fue desarrollado como proyecto académico para aplicar conceptos de desarrollo de software, gestión de requisitos, historias de usuario, planificación mediante sprints y control de versiones.

### 3. Guarda

Presiona:

**Ctrl + S**

Y asegúrate de que **ya no aparezca ninguna de estas líneas**:

```text
<<<<<<< HEAD
=======
>>>>>>> 2d958fd