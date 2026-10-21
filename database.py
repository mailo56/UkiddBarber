import os
import sqlite3
from contextlib import contextmanager

# Ruta absoluta: la base de datos queda junto al código, sin importar
# desde qué carpeta se ejecute la aplicación.
DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "database.db"
)


def conectar():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row

    # SQLite no aplica las claves foráneas a menos que se active.
    conexion.execute("PRAGMA foreign_keys = ON")

    return conexion


@contextmanager
def conexion_bd():
    """
    Entrega una conexión dentro de una transacción.

    - Si el bloque termina bien, se hace commit.
    - Si ocurre una excepción, se hace rollback.
    - La conexión siempre se cierra.
    """
    conexion = conectar()

    try:
        with conexion:
            yield conexion
    finally:
        conexion.close()


def crear_bd():
    conexion = conectar()

    conexion.executescript("""
        CREATE TABLE IF NOT EXISTS cliente (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            correo TEXT
        );

        CREATE TABLE IF NOT EXISTS servicio (
            id_servicio INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio INTEGER NOT NULL,
            duracion INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS barbero (
            id_barbero INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS disponibilidad (
            id_disponibilidad INTEGER PRIMARY KEY AUTOINCREMENT,
            id_barbero INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            disponible INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (id_barbero) REFERENCES barbero(id_barbero)
        );

        CREATE TABLE IF NOT EXISTS reserva (
            id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            id_barbero INTEGER NOT NULL,
            id_servicio INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Confirmada',
            FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
            FOREIGN KEY (id_barbero) REFERENCES barbero(id_barbero),
            FOREIGN KEY (id_servicio) REFERENCES servicio(id_servicio)
        );
    """)

    # Índices únicos: garantizan a nivel de base de datos que no existan
    # horarios duplicados ni dos reservas confirmadas en el mismo horario.
    # Se crean aparte para que también apliquen a bases de datos ya existentes.
    indices = [
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_disponibilidad_unica
        ON disponibilidad (id_barbero, fecha, hora)
        """,
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_reserva_confirmada_unica
        ON reserva (id_barbero, fecha, hora)
        WHERE estado = 'Confirmada'
        """,
    ]

    for sentencia in indices:
        try:
            conexion.execute(sentencia)
        except sqlite3.IntegrityError:
            # La base de datos ya tiene datos duplicados; hay que
            # limpiarlos a mano antes de poder crear el índice.
            print(
                "AVISO: no se pudo crear un índice único porque ya "
                "existen registros duplicados en la base de datos."
            )

    conexion.commit()
    conexion.close()


if __name__ == "__main__":
    crear_bd()
    print("Base de datos creada correctamente.")
