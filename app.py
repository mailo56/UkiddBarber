import hmac
import os
import re
import sqlite3
from datetime import datetime

from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from database import conexion_bd, crear_bd

app = Flask(__name__)

# ---------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------
# Define estas variables de entorno antes de ejecutar:
#   UKIDD_ADMIN_PASSWORD  -> contraseña del panel de administración
#   UKIDD_SECRET_KEY      -> (opcional) clave para firmar las sesiones;
#                            si no se define, se genera una al iniciar
#                            (las sesiones se cierran al reiniciar).

CLAVE_ADMIN = os.environ.get("UKIDD_ADMIN_PASSWORD", "")

app.secret_key = os.environ.get("UKIDD_SECRET_KEY") or os.urandom(32)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    # Lax evita que otros sitios puedan enviar formularios POST
    # usando la sesión del administrador (protección básica contra CSRF).
    SESSION_COOKIE_SAMESITE="Lax",
)

# Rutas accesibles sin iniciar sesión. Todo lo demás es solo para el
# administrador, de modo que una ruta nueva queda protegida por defecto.
RUTAS_PUBLICAS = {
    "inicio",
    "reservar_publico",
    "api_horarios",
    "login_admin",
    "static",
}


# =========================================================
# ERRORES Y VALIDACIÓN
# =========================================================

class ErrorFormulario(Exception):
    """Error de datos ingresados por el usuario (se muestra en pantalla)."""


@app.errorhandler(ErrorFormulario)
def manejar_error_formulario(error):
    volver = request.referrer

    if not volver or not volver.startswith(request.host_url):
        volver = url_for("inicio")

    return render_template(
        "mensaje.html",
        titulo="No se pudo completar la acción",
        texto=str(error),
        enlace=volver,
        texto_enlace="Volver",
    ), 400


@app.errorhandler(sqlite3.IntegrityError)
def manejar_error_integridad(error):
    return render_template(
        "mensaje.html",
        titulo="No se pudo completar la acción",
        texto=(
            "Los datos no son válidos o entran en conflicto con "
            "información ya registrada (por ejemplo, un horario ya ocupado)."
        ),
        enlace=url_for("inicio"),
        texto_enlace="Volver al inicio",
    ), 400


@app.errorhandler(404)
def manejar_no_encontrado(error):
    return render_template(
        "mensaje.html",
        titulo="Página no encontrada",
        texto="El recurso que buscas no existe.",
        enlace=url_for("inicio"),
        texto_enlace="Volver al inicio",
    ), 404


def campo_texto(nombre, etiqueta, maximo=80, obligatorio=True):
    valor = request.form.get(nombre, "").strip()

    if not valor:
        if obligatorio:
            raise ErrorFormulario(f"El campo «{etiqueta}» es obligatorio.")
        return None

    if len(valor) > maximo:
        raise ErrorFormulario(
            f"El campo «{etiqueta}» admite hasta {maximo} caracteres."
        )

    return valor


def campo_entero(nombre, etiqueta, minimo, maximo):
    try:
        valor = int(request.form.get(nombre, "").strip())
    except ValueError:
        raise ErrorFormulario(f"«{etiqueta}» debe ser un número entero.")

    if not minimo <= valor <= maximo:
        raise ErrorFormulario(
            f"«{etiqueta}» debe estar entre {minimo} y {maximo}."
        )

    return valor


def campo_id(nombre, etiqueta):
    return campo_entero(nombre, etiqueta, 1, 2_147_483_647)


def campo_telefono():
    valor = campo_texto("telefono", "Teléfono", maximo=20)

    if not re.fullmatch(r"\+?[0-9 ()\-]{7,20}", valor):
        raise ErrorFormulario("El teléfono ingresado no es válido.")

    return valor


def campo_correo(obligatorio):
    valor = campo_texto(
        "correo", "Correo", maximo=120, obligatorio=obligatorio
    )

    if valor is None:
        return None

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
        raise ErrorFormulario("El correo ingresado no es válido.")

    return valor.lower()


def campo_fecha():
    valor = request.form.get("fecha", "").strip()

    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ErrorFormulario("La fecha ingresada no es válida.")


def campo_hora():
    valor = request.form.get("hora", "").strip()

    try:
        return datetime.strptime(valor, "%H:%M").strftime("%H:%M")
    except ValueError:
        raise ErrorFormulario("La hora ingresada no es válida.")


def validar_no_pasado(fecha, hora):
    momento = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")

    if momento < datetime.now():
        raise ErrorFormulario(
            "No se puede usar una fecha y hora que ya pasaron."
        )


# =========================================================
# FUNCIONES AUXILIARES DE BASE DE DATOS
# =========================================================

def listar_clientes(conexion):
    return conexion.execute(
        "SELECT * FROM cliente ORDER BY nombre"
    ).fetchall()


def listar_servicios(conexion):
    return conexion.execute(
        "SELECT * FROM servicio ORDER BY nombre"
    ).fetchall()


def listar_barberos(conexion):
    return conexion.execute(
        "SELECT * FROM barbero ORDER BY nombre"
    ).fetchall()


def consultar_reservas(conexion):
    return conexion.execute(
        """
        SELECT
            reserva.id_reserva,
            reserva.id_cliente,
            reserva.id_servicio,
            reserva.id_barbero,
            cliente.nombre AS nombre_cliente,
            servicio.nombre AS nombre_servicio,
            barbero.nombre AS nombre_barbero,
            reserva.fecha,
            reserva.hora,
            reserva.estado
        FROM reserva
        INNER JOIN cliente
            ON reserva.id_cliente = cliente.id_cliente
        INNER JOIN servicio
            ON reserva.id_servicio = servicio.id_servicio
        INNER JOIN barbero
            ON reserva.id_barbero = barbero.id_barbero
        ORDER BY reserva.fecha, reserva.hora
        """
    ).fetchall()


def tiene_reservas(conexion, columna, valor):
    # "columna" siempre viene del código, nunca del usuario.
    if columna not in ("id_cliente", "id_servicio", "id_barbero"):
        raise ValueError("Columna no permitida")

    fila = conexion.execute(
        f"SELECT COUNT(*) AS total FROM reserva WHERE {columna} = ?",
        (valor,)
    ).fetchone()

    return fila["total"] > 0


def ocupar_horario(conexion, id_barbero, fecha, hora):
    """
    Marca el horario como ocupado en una sola operación atómica.
    Evita que dos personas reserven el mismo horario a la vez.
    Devuelve True si se logró ocupar.
    """
    cursor = conexion.execute(
        """
        UPDATE disponibilidad
        SET disponible = 0
        WHERE id_barbero = ?
        AND fecha = ?
        AND hora = ?
        AND disponible = 1
        """,
        (id_barbero, fecha, hora)
    )

    return cursor.rowcount == 1


def liberar_horario(conexion, id_barbero, fecha, hora):
    conexion.execute(
        """
        UPDATE disponibilidad
        SET disponible = 1
        WHERE id_barbero = ?
        AND fecha = ?
        AND hora = ?
        """,
        (id_barbero, fecha, hora)
    )


# =========================================================
# ACCESO DE ADMINISTRADOR
# =========================================================

@app.before_request
def exigir_login():
    if request.endpoint is None or request.endpoint in RUTAS_PUBLICAS:
        return None

    if session.get("admin"):
        return None

    if request.method == "GET":
        return redirect(url_for("login_admin", next=request.full_path))

    return redirect(url_for("login_admin"))


def destino_seguro(destino):
    """Solo permite redirigir a rutas internas del propio sitio."""
    if (
        destino
        and destino.startswith("/")
        and not destino.startswith("//")
        and "\\" not in destino
    ):
        return destino

    return url_for("agenda")


@app.route("/admin/login", methods=["GET", "POST"])
def login_admin():
    error = None

    if request.method == "POST":

        if not CLAVE_ADMIN:
            error = (
                "No hay contraseña de administrador configurada. "
                "Define la variable de entorno UKIDD_ADMIN_PASSWORD "
                "y reinicia la aplicación."
            )

        elif hmac.compare_digest(
            request.form.get("clave", "").encode(),
            CLAVE_ADMIN.encode()
        ):
            session.clear()
            session["admin"] = True

            return redirect(destino_seguro(request.args.get("next")))

        else:
            error = "Contraseña incorrecta."

    return render_template("login.html", error=error), (
        401 if error else 200
    )


@app.route("/admin/logout", methods=["POST"])
def logout_admin():
    session.clear()
    return redirect(url_for("inicio"))


# =========================================================
# INICIO
# =========================================================

@app.route("/")
def inicio():
    with conexion_bd() as conexion:
        servicios = listar_servicios(conexion)
        barberos = listar_barberos(conexion)

    return render_template(
        "inicio.html",
        servicios=servicios,
        barberos=barberos
    )


# =========================================================
# US01 — GESTIÓN DE CLIENTES
# =========================================================

@app.route("/clientes")
def clientes():
    with conexion_bd() as conexion:
        clientes = conexion.execute(
            "SELECT * FROM cliente ORDER BY id_cliente DESC"
        ).fetchall()

    return render_template(
        "clientes.html",
        clientes=clientes
    )


@app.route("/clientes/agregar", methods=["POST"])
def agregar_cliente():
    nombre = campo_texto("nombre", "Nombre")
    telefono = campo_telefono()
    correo = campo_correo(obligatorio=False)

    with conexion_bd() as conexion:
        conexion.execute(
            """
            INSERT INTO cliente (nombre, telefono, correo)
            VALUES (?, ?, ?)
            """,
            (nombre, telefono, correo)
        )

    return redirect(url_for("clientes"))


@app.route("/clientes/editar/<int:id_cliente>", methods=["GET", "POST"])
def editar_cliente(id_cliente):
    with conexion_bd() as conexion:
        cliente = conexion.execute(
            "SELECT * FROM cliente WHERE id_cliente = ?",
            (id_cliente,)
        ).fetchone()

        if cliente is None:
            abort(404)

        if request.method == "POST":
            nombre = campo_texto("nombre", "Nombre")
            telefono = campo_telefono()
            correo = campo_correo(obligatorio=False)

            conexion.execute(
                """
                UPDATE cliente
                SET nombre = ?, telefono = ?, correo = ?
                WHERE id_cliente = ?
                """,
                (nombre, telefono, correo, id_cliente)
            )

            return redirect(url_for("clientes"))

    return render_template(
        "editar_cliente.html",
        cliente=cliente
    )


@app.route("/clientes/eliminar/<int:id_cliente>", methods=["POST"])
def eliminar_cliente(id_cliente):
    with conexion_bd() as conexion:
        if tiene_reservas(conexion, "id_cliente", id_cliente):
            raise ErrorFormulario(
                "No se puede eliminar un cliente que tiene reservas "
                "registradas."
            )

        conexion.execute(
            "DELETE FROM cliente WHERE id_cliente = ?",
            (id_cliente,)
        )

    return redirect(url_for("clientes"))


# =========================================================
# US02 — GESTIÓN DE SERVICIOS
# =========================================================

@app.route("/servicios")
def servicios():
    with conexion_bd() as conexion:
        servicios = conexion.execute(
            "SELECT * FROM servicio ORDER BY id_servicio DESC"
        ).fetchall()

    return render_template(
        "servicios.html",
        servicios=servicios
    )


@app.route("/servicios/agregar", methods=["POST"])
def agregar_servicio():
    nombre = campo_texto("nombre", "Nombre")
    precio = campo_entero("precio", "Precio", 1, 10_000_000)
    duracion = campo_entero("duracion", "Duración (minutos)", 5, 480)

    with conexion_bd() as conexion:
        conexion.execute(
            """
            INSERT INTO servicio (nombre, precio, duracion)
            VALUES (?, ?, ?)
            """,
            (nombre, precio, duracion)
        )

    return redirect(url_for("servicios"))


@app.route("/servicios/editar/<int:id_servicio>", methods=["GET", "POST"])
def editar_servicio(id_servicio):
    with conexion_bd() as conexion:
        servicio = conexion.execute(
            "SELECT * FROM servicio WHERE id_servicio = ?",
            (id_servicio,)
        ).fetchone()

        if servicio is None:
            abort(404)

        if request.method == "POST":
            nombre = campo_texto("nombre", "Nombre")
            precio = campo_entero("precio", "Precio", 1, 10_000_000)
            duracion = campo_entero(
                "duracion", "Duración (minutos)", 5, 480
            )

            conexion.execute(
                """
                UPDATE servicio
                SET nombre = ?, precio = ?, duracion = ?
                WHERE id_servicio = ?
                """,
                (nombre, precio, duracion, id_servicio)
            )

            return redirect(url_for("servicios"))

    return render_template(
        "editar_servicio.html",
        servicio=servicio
    )


@app.route("/servicios/eliminar/<int:id_servicio>", methods=["POST"])
def eliminar_servicio(id_servicio):
    with conexion_bd() as conexion:
        if tiene_reservas(conexion, "id_servicio", id_servicio):
            raise ErrorFormulario(
                "No se puede eliminar un servicio que tiene reservas "
                "registradas."
            )

        conexion.execute(
            "DELETE FROM servicio WHERE id_servicio = ?",
            (id_servicio,)
        )

    return redirect(url_for("servicios"))


# =========================================================
# US03 — GESTIÓN DE BARBEROS
# =========================================================

@app.route("/barberos")
def barberos():
    with conexion_bd() as conexion:
        barberos = conexion.execute(
            "SELECT * FROM barbero ORDER BY id_barbero DESC"
        ).fetchall()

    return render_template(
        "barberos.html",
        barberos=barberos
    )


@app.route("/barberos/agregar", methods=["POST"])
def agregar_barbero():
    nombre = campo_texto("nombre", "Nombre")

    with conexion_bd() as conexion:
        conexion.execute(
            "INSERT INTO barbero (nombre) VALUES (?)",
            (nombre,)
        )

    return redirect(url_for("barberos"))


@app.route("/barberos/editar/<int:id_barbero>", methods=["GET", "POST"])
def editar_barbero(id_barbero):
    with conexion_bd() as conexion:
        barbero = conexion.execute(
            "SELECT * FROM barbero WHERE id_barbero = ?",
            (id_barbero,)
        ).fetchone()

        if barbero is None:
            abort(404)

        if request.method == "POST":
            nombre = campo_texto("nombre", "Nombre")

            conexion.execute(
                "UPDATE barbero SET nombre = ? WHERE id_barbero = ?",
                (nombre, id_barbero)
            )

            return redirect(url_for("barberos"))

    return render_template(
        "editar_barbero.html",
        barbero=barbero
    )


@app.route("/barberos/eliminar/<int:id_barbero>", methods=["POST"])
def eliminar_barbero(id_barbero):
    with conexion_bd() as conexion:
        if tiene_reservas(conexion, "id_barbero", id_barbero):
            raise ErrorFormulario(
                "No se puede eliminar un barbero que tiene reservas "
                "registradas."
            )

        # Sin reservas, sus horarios publicados ya no sirven.
        conexion.execute(
            "DELETE FROM disponibilidad WHERE id_barbero = ?",
            (id_barbero,)
        )

        conexion.execute(
            "DELETE FROM barbero WHERE id_barbero = ?",
            (id_barbero,)
        )

    return redirect(url_for("barberos"))


# =========================================================
# US04 — GESTIÓN DE DISPONIBILIDAD
# =========================================================

@app.route("/disponibilidad")
def disponibilidad():
    with conexion_bd() as conexion:
        barberos = listar_barberos(conexion)

        disponibilidades = conexion.execute(
            """
            SELECT
                disponibilidad.id_disponibilidad,
                disponibilidad.fecha,
                disponibilidad.hora,
                disponibilidad.disponible,
                barbero.nombre AS nombre_barbero
            FROM disponibilidad
            INNER JOIN barbero
                ON disponibilidad.id_barbero = barbero.id_barbero
            ORDER BY disponibilidad.fecha, disponibilidad.hora
            """
        ).fetchall()

    return render_template(
        "disponibilidad.html",
        barberos=barberos,
        disponibilidades=disponibilidades
    )


@app.route("/disponibilidad/agregar", methods=["POST"])
def agregar_disponibilidad():
    id_barbero = campo_id("id_barbero", "Barbero")
    fecha = campo_fecha()
    hora = campo_hora()

    validar_no_pasado(fecha, hora)

    with conexion_bd() as conexion:
        barbero = conexion.execute(
            "SELECT 1 FROM barbero WHERE id_barbero = ?",
            (id_barbero,)
        ).fetchone()

        if barbero is None:
            raise ErrorFormulario("El barbero seleccionado no existe.")

        try:
            conexion.execute(
                """
                INSERT INTO disponibilidad
                (id_barbero, fecha, hora, disponible)
                VALUES (?, ?, ?, 1)
                """,
                (id_barbero, fecha, hora)
            )
        except sqlite3.IntegrityError:
            raise ErrorFormulario(
                "Ese horario ya está registrado para el barbero."
            )

    return redirect(url_for("disponibilidad"))


@app.route(
    "/disponibilidad/eliminar/<int:id_disponibilidad>",
    methods=["POST"]
)
def eliminar_disponibilidad(id_disponibilidad):
    with conexion_bd() as conexion:
        horario = conexion.execute(
            "SELECT * FROM disponibilidad WHERE id_disponibilidad = ?",
            (id_disponibilidad,)
        ).fetchone()

        if horario is None:
            abort(404)

        if horario["disponible"] == 0:
            raise ErrorFormulario(
                "Este horario tiene una reserva confirmada. "
                "Cancela la reserva antes de eliminarlo."
            )

        conexion.execute(
            "DELETE FROM disponibilidad WHERE id_disponibilidad = ?",
            (id_disponibilidad,)
        )

    return redirect(url_for("disponibilidad"))


# =========================================================
# US05 — CREAR RESERVA
# =========================================================

@app.route("/reservas")
def reservas():
    with conexion_bd() as conexion:
        clientes = listar_clientes(conexion)
        servicios = listar_servicios(conexion)
        barberos = listar_barberos(conexion)
        reservas = consultar_reservas(conexion)

    return render_template(
        "reservas.html",
        clientes=clientes,
        servicios=servicios,
        barberos=barberos,
        reservas=reservas
    )


@app.route("/reservas/agregar", methods=["POST"])
def agregar_reserva():
    id_cliente = campo_id("id_cliente", "Cliente")
    id_servicio = campo_id("id_servicio", "Servicio")
    id_barbero = campo_id("id_barbero", "Barbero")
    fecha = campo_fecha()
    hora = campo_hora()

    validar_no_pasado(fecha, hora)

    with conexion_bd() as conexion:
        if not ocupar_horario(conexion, id_barbero, fecha, hora):
            raise ErrorFormulario(
                "El horario seleccionado no está disponible."
            )

        conexion.execute(
            """
            INSERT INTO reserva
            (id_cliente, id_barbero, id_servicio, fecha, hora, estado)
            VALUES (?, ?, ?, ?, ?, 'Confirmada')
            """,
            (id_cliente, id_barbero, id_servicio, fecha, hora)
        )

    return redirect(url_for("reservas"))


# =========================================================
# US06 — MODIFICAR RESERVA
# =========================================================

@app.route(
    "/reservas/editar/<int:id_reserva>",
    methods=["GET", "POST"]
)
def editar_reserva(id_reserva):
    with conexion_bd() as conexion:
        reserva = conexion.execute(
            "SELECT * FROM reserva WHERE id_reserva = ?",
            (id_reserva,)
        ).fetchone()

        if reserva is None:
            abort(404)

        if reserva["estado"] != "Confirmada":
            raise ErrorFormulario(
                "Solo se pueden modificar reservas confirmadas."
            )

        if request.method == "POST":
            id_cliente = campo_id("id_cliente", "Cliente")
            id_servicio = campo_id("id_servicio", "Servicio")
            id_barbero = campo_id("id_barbero", "Barbero")
            fecha = campo_fecha()
            hora = campo_hora()

            cambia_horario = (
                id_barbero != reserva["id_barbero"]
                or fecha != reserva["fecha"]
                or hora != reserva["hora"]
            )

            if cambia_horario:
                validar_no_pasado(fecha, hora)

                if not ocupar_horario(conexion, id_barbero, fecha, hora):
                    raise ErrorFormulario(
                        "El nuevo horario no está disponible."
                    )

                liberar_horario(
                    conexion,
                    reserva["id_barbero"],
                    reserva["fecha"],
                    reserva["hora"]
                )

            conexion.execute(
                """
                UPDATE reserva
                SET
                    id_cliente = ?,
                    id_barbero = ?,
                    id_servicio = ?,
                    fecha = ?,
                    hora = ?
                WHERE id_reserva = ?
                """,
                (
                    id_cliente,
                    id_barbero,
                    id_servicio,
                    fecha,
                    hora,
                    id_reserva
                )
            )

            return redirect(url_for("reservas"))

        clientes = listar_clientes(conexion)
        servicios = listar_servicios(conexion)
        barberos = listar_barberos(conexion)

    return render_template(
        "editar_reserva.html",
        reserva=reserva,
        clientes=clientes,
        servicios=servicios,
        barberos=barberos
    )


# =========================================================
# US07 — CANCELAR RESERVA
# =========================================================

@app.route(
    "/reservas/cancelar/<int:id_reserva>",
    methods=["POST"]
)
def cancelar_reserva(id_reserva):
    with conexion_bd() as conexion:
        reserva = conexion.execute(
            "SELECT * FROM reserva WHERE id_reserva = ?",
            (id_reserva,)
        ).fetchone()

        if reserva is None:
            abort(404)

        # Si ya estaba cancelada no se libera el horario otra vez:
        # podría pertenecer ahora a otra reserva.
        if reserva["estado"] == "Confirmada":
            conexion.execute(
                "UPDATE reserva SET estado = 'Cancelada' "
                "WHERE id_reserva = ?",
                (id_reserva,)
            )

            liberar_horario(
                conexion,
                reserva["id_barbero"],
                reserva["fecha"],
                reserva["hora"]
            )

    return redirect(url_for("reservas"))


# =========================================================
# US08 — VISUALIZAR AGENDA
# =========================================================

@app.route("/agenda")
def agenda():
    with conexion_bd() as conexion:
        reservas = consultar_reservas(conexion)

    return render_template(
        "agenda.html",
        reservas=reservas
    )


# =========================================================
# RESERVA PÚBLICA
# =========================================================

@app.route("/reservar", methods=["GET", "POST"])
def reservar_publico():
    if request.method == "POST":
        nombre = campo_texto("nombre", "Nombre")
        telefono = campo_telefono()
        correo = campo_correo(obligatorio=True)

        id_servicio = campo_id("id_servicio", "Servicio")
        id_barbero = campo_id("id_barbero", "Barbero")
        fecha = campo_fecha()
        hora = campo_hora()

        validar_no_pasado(fecha, hora)

        with conexion_bd() as conexion:
            # Ocupar el horario primero: si otra persona lo tomó antes,
            # no se crea nada.
            if not ocupar_horario(conexion, id_barbero, fecha, hora):
                raise ErrorFormulario(
                    "El horario seleccionado ya no está disponible."
                )

            cliente = conexion.execute(
                "SELECT * FROM cliente WHERE correo = ?",
                (correo,)
            ).fetchone()

            if cliente is None:
                cursor = conexion.execute(
                    """
                    INSERT INTO cliente (nombre, telefono, correo)
                    VALUES (?, ?, ?)
                    """,
                    (nombre, telefono, correo)
                )

                id_cliente = cursor.lastrowid

            else:
                id_cliente = cliente["id_cliente"]

                conexion.execute(
                    """
                    UPDATE cliente
                    SET nombre = ?, telefono = ?
                    WHERE id_cliente = ?
                    """,
                    (nombre, telefono, id_cliente)
                )

            conexion.execute(
                """
                INSERT INTO reserva
                (id_cliente, id_barbero, id_servicio, fecha, hora, estado)
                VALUES (?, ?, ?, ?, ?, 'Confirmada')
                """,
                (id_cliente, id_barbero, id_servicio, fecha, hora)
            )

        return render_template(
            "mensaje.html",
            titulo="¡Reserva confirmada!",
            texto=(
                f"Tu hora fue reservada para el {fecha} a las {hora}. "
                "¡Te esperamos!"
            ),
            enlace=url_for("inicio"),
            texto_enlace="Volver al inicio",
        )

    with conexion_bd() as conexion:
        servicios = listar_servicios(conexion)
        barberos = listar_barberos(conexion)

    return render_template(
        "reservar.html",
        servicios=servicios,
        barberos=barberos,
        hoy=datetime.now().strftime("%Y-%m-%d")
    )


# =========================================================
# API — HORARIOS DISPONIBLES
# =========================================================

@app.route("/api/horarios")
def api_horarios():
    try:
        id_barbero = int(request.args.get("id_barbero", ""))
        fecha = datetime.strptime(
            request.args.get("fecha", ""), "%Y-%m-%d"
        ).strftime("%Y-%m-%d")
    except ValueError:
        return jsonify([])

    ahora = datetime.now()
    hoy = ahora.strftime("%Y-%m-%d")

    if fecha < hoy:
        return jsonify([])

    with conexion_bd() as conexion:
        filas = conexion.execute(
            """
            SELECT hora
            FROM disponibilidad
            WHERE id_barbero = ?
            AND fecha = ?
            AND disponible = 1
            ORDER BY hora
            """,
            (id_barbero, fecha)
        ).fetchall()

    horarios = [{"hora": fila["hora"]} for fila in filas]

    # Para el día de hoy, ocultar las horas que ya pasaron.
    if fecha == hoy:
        hora_actual = ahora.strftime("%H:%M")
        horarios = [h for h in horarios if h["hora"] > hora_actual]

    return jsonify(horarios)


# =========================================================
# EJECUTAR APLICACIÓN
# =========================================================

# Se crea la base de datos al importar el módulo, para que también
# funcione con `flask run` o un servidor de producción.
crear_bd()

if __name__ == "__main__":
    # El modo debug solo se activa si se pide explícitamente:
    #   set FLASK_DEBUG=1   (Windows)   /   export FLASK_DEBUG=1   (Linux/Mac)
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
