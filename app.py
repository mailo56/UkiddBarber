from flask import Flask, render_template, request, redirect, url_for
from database import conectar, crear_bd

app = Flask(__name__)


# =========================================================
# INICIO
# =========================================================

@app.route("/")
def inicio():
    conexion = conectar()

    servicios = conexion.execute(
        """
        SELECT *
        FROM servicio
        ORDER BY nombre
        """
    ).fetchall()

    barberos = conexion.execute(
        """
        SELECT *
        FROM barbero
        ORDER BY nombre
        """
    ).fetchall()

    conexion.close()

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
    conexion = conectar()

    clientes = conexion.execute(
        "SELECT * FROM cliente ORDER BY id_cliente DESC"
    ).fetchall()

    conexion.close()

    return render_template(
        "clientes.html",
        clientes=clientes
    )


@app.route("/clientes/agregar", methods=["POST"])
def agregar_cliente():
    nombre = request.form["nombre"]
    telefono = request.form["telefono"]
    correo = request.form["correo"]

    conexion = conectar()

    conexion.execute(
        """
        INSERT INTO cliente (nombre, telefono, correo)
        VALUES (?, ?, ?)
        """,
        (nombre, telefono, correo)
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("clientes"))


@app.route("/clientes/editar/<int:id_cliente>", methods=["GET", "POST"])
def editar_cliente(id_cliente):
    conexion = conectar()

    cliente = conexion.execute(
        """
        SELECT *
        FROM cliente
        WHERE id_cliente = ?
        """,
        (id_cliente,)
    ).fetchone()

    if cliente is None:
        conexion.close()
        return "Cliente no encontrado", 404

    if request.method == "POST":

        nombre = request.form["nombre"]
        telefono = request.form["telefono"]
        correo = request.form["correo"]

        conexion.execute(
            """
            UPDATE cliente
            SET nombre = ?, telefono = ?, correo = ?
            WHERE id_cliente = ?
            """,
            (nombre, telefono, correo, id_cliente)
        )

        conexion.commit()
        conexion.close()

        return redirect(url_for("clientes"))

    conexion.close()

    return render_template(
        "editar_cliente.html",
        cliente=cliente
    )


@app.route("/clientes/eliminar/<int:id_cliente>", methods=["POST"])
def eliminar_cliente(id_cliente):
    conexion = conectar()

    conexion.execute(
        """
        DELETE FROM cliente
        WHERE id_cliente = ?
        """,
        (id_cliente,)
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("clientes"))


# =========================================================
# US02 — GESTIÓN DE SERVICIOS
# =========================================================

@app.route("/servicios")
def servicios():
    conexion = conectar()

    servicios = conexion.execute(
        """
        SELECT *
        FROM servicio
        ORDER BY id_servicio DESC
        """
    ).fetchall()

    conexion.close()

    return render_template(
        "servicios.html",
        servicios=servicios
    )


@app.route("/servicios/agregar", methods=["POST"])
def agregar_servicio():
    nombre = request.form["nombre"]
    precio = request.form["precio"]
    duracion = request.form["duracion"]

    conexion = conectar()

    conexion.execute(
        """
        INSERT INTO servicio (nombre, precio, duracion)
        VALUES (?, ?, ?)
        """,
        (nombre, precio, duracion)
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("servicios"))


@app.route("/servicios/editar/<int:id_servicio>", methods=["GET", "POST"])
def editar_servicio(id_servicio):
    conexion = conectar()

    servicio = conexion.execute(
        """
        SELECT *
        FROM servicio
        WHERE id_servicio = ?
        """,
        (id_servicio,)
    ).fetchone()

    if servicio is None:
        conexion.close()
        return "Servicio no encontrado", 404

    if request.method == "POST":

        nombre = request.form["nombre"]
        precio = request.form["precio"]
        duracion = request.form["duracion"]

        conexion.execute(
            """
            UPDATE servicio
            SET nombre = ?, precio = ?, duracion = ?
            WHERE id_servicio = ?
            """,
            (nombre, precio, duracion, id_servicio)
        )

        conexion.commit()
        conexion.close()

        return redirect(url_for("servicios"))

    conexion.close()

    return render_template(
        "editar_servicio.html",
        servicio=servicio
    )


@app.route("/servicios/eliminar/<int:id_servicio>", methods=["POST"])
def eliminar_servicio(id_servicio):
    conexion = conectar()

    conexion.execute(
        """
        DELETE FROM servicio
        WHERE id_servicio = ?
        """,
        (id_servicio,)
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("servicios"))


# =========================================================
# US03 — GESTIÓN DE BARBEROS
# =========================================================

@app.route("/barberos")
def barberos():
    conexion = conectar()

    barberos = conexion.execute(
        """
        SELECT *
        FROM barbero
        ORDER BY id_barbero DESC
        """
    ).fetchall()

    conexion.close()

    return render_template(
        "barberos.html",
        barberos=barberos
    )


@app.route("/barberos/agregar", methods=["POST"])
def agregar_barbero():
    nombre = request.form["nombre"]

    conexion = conectar()

    conexion.execute(
        """
        INSERT INTO barbero (nombre)
        VALUES (?)
        """,
        (nombre,)
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("barberos"))


@app.route("/barberos/editar/<int:id_barbero>", methods=["GET", "POST"])
def editar_barbero(id_barbero):
    conexion = conectar()

    barbero = conexion.execute(
        """
        SELECT *
        FROM barbero
        WHERE id_barbero = ?
        """,
        (id_barbero,)
    ).fetchone()

    if barbero is None:
        conexion.close()
        return "Barbero no encontrado", 404

    if request.method == "POST":

        nombre = request.form["nombre"]

        conexion.execute(
            """
            UPDATE barbero
            SET nombre = ?
            WHERE id_barbero = ?
            """,
            (nombre, id_barbero)
        )

        conexion.commit()
        conexion.close()

        return redirect(url_for("barberos"))

    conexion.close()

    return render_template(
        "editar_barbero.html",
        barbero=barbero
    )


@app.route("/barberos/eliminar/<int:id_barbero>", methods=["POST"])
def eliminar_barbero(id_barbero):
    conexion = conectar()

    conexion.execute(
        """
        DELETE FROM barbero
        WHERE id_barbero = ?
        """,
        (id_barbero,)
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("barberos"))


# =========================================================
# US04 — GESTIÓN DE DISPONIBILIDAD
# =========================================================

@app.route("/disponibilidad")
def disponibilidad():
    conexion = conectar()

    barberos = conexion.execute(
        """
        SELECT *
        FROM barbero
        ORDER BY nombre
        """
    ).fetchall()

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

    conexion.close()

    return render_template(
        "disponibilidad.html",
        barberos=barberos,
        disponibilidades=disponibilidades
    )


@app.route("/disponibilidad/agregar", methods=["POST"])
def agregar_disponibilidad():
    id_barbero = request.form["id_barbero"]
    fecha = request.form["fecha"]
    hora = request.form["hora"]

    conexion = conectar()

    conexion.execute(
        """
        INSERT INTO disponibilidad
        (id_barbero, fecha, hora, disponible)
        VALUES (?, ?, ?, 1)
        """,
        (id_barbero, fecha, hora)
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("disponibilidad"))


@app.route(
    "/disponibilidad/eliminar/<int:id_disponibilidad>",
    methods=["POST"]
)
def eliminar_disponibilidad(id_disponibilidad):
    conexion = conectar()

    conexion.execute(
        """
        DELETE FROM disponibilidad
        WHERE id_disponibilidad = ?
        """,
        (id_disponibilidad,)
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("disponibilidad"))


# =========================================================
# US05 — CREAR RESERVA
# =========================================================

@app.route("/reservas")
def reservas():
    conexion = conectar()

    clientes = conexion.execute(
        """
        SELECT *
        FROM cliente
        ORDER BY nombre
        """
    ).fetchall()

    servicios = conexion.execute(
        """
        SELECT *
        FROM servicio
        ORDER BY nombre
        """
    ).fetchall()

    barberos = conexion.execute(
        """
        SELECT *
        FROM barbero
        ORDER BY nombre
        """
    ).fetchall()

    reservas = conexion.execute(
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

    conexion.close()

    return render_template(
        "reservas.html",
        clientes=clientes,
        servicios=servicios,
        barberos=barberos,
        reservas=reservas
    )


@app.route("/reservas/agregar", methods=["POST"])
def agregar_reserva():
    id_cliente = request.form["id_cliente"]
    id_servicio = request.form["id_servicio"]
    id_barbero = request.form["id_barbero"]
    fecha = request.form["fecha"]
    hora = request.form["hora"]

    conexion = conectar()

    disponibilidad = conexion.execute(
        """
        SELECT *
        FROM disponibilidad
        WHERE id_barbero = ?
        AND fecha = ?
        AND hora = ?
        AND disponible = 1
        """,
        (id_barbero, fecha, hora)
    ).fetchone()

    if disponibilidad is None:
        conexion.close()
        return "El horario seleccionado no está disponible.", 400

    conexion.execute(
        """
        INSERT INTO reserva
        (
            id_cliente,
            id_barbero,
            id_servicio,
            fecha,
            hora,
            estado
        )
        VALUES (?, ?, ?, ?, ?, 'Confirmada')
        """,
        (
            id_cliente,
            id_barbero,
            id_servicio,
            fecha,
            hora
        )
    )

    conexion.execute(
        """
        UPDATE disponibilidad
        SET disponible = 0
        WHERE id_disponibilidad = ?
        """,
        (disponibilidad["id_disponibilidad"],)
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("reservas"))


# =========================================================
# US06 — MODIFICAR RESERVA
# =========================================================

@app.route(
    "/reservas/editar/<int:id_reserva>",
    methods=["GET", "POST"]
)
def editar_reserva(id_reserva):
    conexion = conectar()

    reserva = conexion.execute(
        """
        SELECT *
        FROM reserva
        WHERE id_reserva = ?
        """,
        (id_reserva,)
    ).fetchone()

    if reserva is None:
        conexion.close()
        return "Reserva no encontrada", 404

    if request.method == "POST":

        id_cliente = request.form["id_cliente"]
        id_servicio = request.form["id_servicio"]
        id_barbero = request.form["id_barbero"]
        fecha = request.form["fecha"]
        hora = request.form["hora"]

        mismo_horario = (
            int(id_barbero) == reserva["id_barbero"]
            and fecha == reserva["fecha"]
            and hora == reserva["hora"]
        )

        if not mismo_horario:

            disponibilidad = conexion.execute(
                """
                SELECT *
                FROM disponibilidad
                WHERE id_barbero = ?
                AND fecha = ?
                AND hora = ?
                AND disponible = 1
                """,
                (id_barbero, fecha, hora)
            ).fetchone()

            if disponibilidad is None:
                conexion.close()
                return "El nuevo horario no está disponible.", 400

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

        if not mismo_horario:

            conexion.execute(
                """
                UPDATE disponibilidad
                SET disponible = 1
                WHERE id_barbero = ?
                AND fecha = ?
                AND hora = ?
                """,
                (
                    reserva["id_barbero"],
                    reserva["fecha"],
                    reserva["hora"]
                )
            )

            conexion.execute(
                """
                UPDATE disponibilidad
                SET disponible = 0
                WHERE id_disponibilidad = ?
                """,
                (disponibilidad["id_disponibilidad"],)
            )

        conexion.commit()
        conexion.close()

        return redirect(url_for("reservas"))

    clientes = conexion.execute(
        """
        SELECT *
        FROM cliente
        ORDER BY nombre
        """
    ).fetchall()

    servicios = conexion.execute(
        """
        SELECT *
        FROM servicio
        ORDER BY nombre
        """
    ).fetchall()

    barberos = conexion.execute(
        """
        SELECT *
        FROM barbero
        ORDER BY nombre
        """
    ).fetchall()

    conexion.close()

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
    conexion = conectar()

    reserva = conexion.execute(
        """
        SELECT *
        FROM reserva
        WHERE id_reserva = ?
        """,
        (id_reserva,)
    ).fetchone()

    if reserva is None:
        conexion.close()
        return "Reserva no encontrada", 404

    conexion.execute(
        """
        UPDATE reserva
        SET estado = 'Cancelada'
        WHERE id_reserva = ?
        """,
        (id_reserva,)
    )

    conexion.execute(
        """
        UPDATE disponibilidad
        SET disponible = 1
        WHERE id_barbero = ?
        AND fecha = ?
        AND hora = ?
        """,
        (
            reserva["id_barbero"],
            reserva["fecha"],
            reserva["hora"]
        )
    )

    conexion.commit()
    conexion.close()

    return redirect(url_for("reservas"))

# =========================================================
# US08 — VISUALIZAR AGENDA
# =========================================================

@app.route("/agenda")
def agenda():
    conexion = conectar()

    reservas = conexion.execute(
        """
        SELECT
            reserva.id_reserva,
            reserva.fecha,
            reserva.hora,
            reserva.estado,
            cliente.nombre AS nombre_cliente,
            servicio.nombre AS nombre_servicio,
            barbero.nombre AS nombre_barbero
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

    conexion.close()

    return render_template(
        "agenda.html",
        reservas=reservas
    )
# =========================================================
# RESERVA PÚBLICA
# =========================================================

@app.route("/reservar", methods=["GET", "POST"])
def reservar_publico():

    conexion = conectar()

    if request.method == "POST":

        nombre = request.form["nombre"]
        telefono = request.form["telefono"]
        correo = request.form["correo"]

        id_servicio = request.form["id_servicio"]
        id_barbero = request.form["id_barbero"]
        fecha = request.form["fecha"]
        hora = request.form["hora"]

        # Comprobar disponibilidad
        disponibilidad = conexion.execute(
            """
            SELECT *
            FROM disponibilidad
            WHERE id_barbero = ?
            AND fecha = ?
            AND hora = ?
            AND disponible = 1
            """,
            (
                id_barbero,
                fecha,
                hora
            )
        ).fetchone()

        if disponibilidad is None:

            conexion.close()

            return """
                <h2>El horario seleccionado ya no está disponible.</h2>
                <a href="/reservar">Volver a reservar</a>
            """, 400


        # Buscar cliente por correo
        cliente = conexion.execute(
            """
            SELECT *
            FROM cliente
            WHERE correo = ?
            """,
            (correo,)
        ).fetchone()


        if cliente is None:

            cursor = conexion.execute(
                """
                INSERT INTO cliente
                (
                    nombre,
                    telefono,
                    correo
                )
                VALUES (?, ?, ?)
                """,
                (
                    nombre,
                    telefono,
                    correo
                )
            )

            id_cliente = cursor.lastrowid

        else:

            id_cliente = cliente["id_cliente"]

            conexion.execute(
                """
                UPDATE cliente
                SET
                    nombre = ?,
                    telefono = ?
                WHERE id_cliente = ?
                """,
                (
                    nombre,
                    telefono,
                    id_cliente
                )
            )


        # Crear reserva
        conexion.execute(
            """
            INSERT INTO reserva
            (
                id_cliente,
                id_barbero,
                id_servicio,
                fecha,
                hora,
                estado
            )
            VALUES (?, ?, ?, ?, ?, 'Confirmada')
            """,
            (
                id_cliente,
                id_barbero,
                id_servicio,
                fecha,
                hora
            )
        )


        # Ocupar horario
        conexion.execute(
            """
            UPDATE disponibilidad
            SET disponible = 0
            WHERE id_disponibilidad = ?
            """,
            (
                disponibilidad["id_disponibilidad"],
            )
        )


        conexion.commit()
        conexion.close()


        return """
            <div style="
                font-family: Arial;
                text-align: center;
                padding: 80px;
            ">

                <h1>¡Reserva confirmada!</h1>

                <p>
                    Tu hora fue reservada correctamente.
                </p>

                <a href="/">
                    Volver al inicio
                </a>

            </div>
        """


    # GET

    servicios = conexion.execute(
        """
        SELECT *
        FROM servicio
        ORDER BY nombre
        """
    ).fetchall()


    barberos = conexion.execute(
        """
        SELECT *
        FROM barbero
        ORDER BY nombre
        """
    ).fetchall()


    conexion.close()


    return render_template(
        "reservar.html",
        servicios=servicios,
        barberos=barberos
    )


# =========================================================
# API — HORARIOS DISPONIBLES
# =========================================================

@app.route("/api/horarios")
def api_horarios():

    id_barbero = request.args.get("id_barbero")
    fecha = request.args.get("fecha")


    if not id_barbero or not fecha:
        return []


    conexion = conectar()


    horarios = conexion.execute(
        """
        SELECT hora
        FROM disponibilidad
        WHERE id_barbero = ?
        AND fecha = ?
        AND disponible = 1
        ORDER BY hora
        """,
        (
            id_barbero,
            fecha
        )
    ).fetchall()


    conexion.close()


    return [
        {
            "hora": horario["hora"]
        }
        for horario in horarios
    ]
# =========================================================
# PRUEBA DE BASE DE DATOS
# =========================================================

@app.route("/prueba-bd")
def prueba_bd():
    conexion = conectar()

    servicios = conexion.execute(
        "SELECT * FROM servicio"
    ).fetchall()

    conexion.close()

    return {
        "mensaje": "Conexión con SQLite funcionando",
        "servicios": [dict(servicio) for servicio in servicios]
    }


# =========================================================
# EJECUTAR APLICACIÓN
# =========================================================

if __name__ == "__main__":
    crear_bd()
    app.run(debug=True)