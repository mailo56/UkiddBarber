import os
import sqlite3
from contextlib import contextmanager

# ============================================================
# CONFIGURACIÓN
# ============================================================

# Si existe DATABASE_URL, se utiliza PostgreSQL (Render).
# Si no existe, se utiliza SQLite local.
DATABASE_URL = os.environ.get("DATABASE_URL")

DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "database.db"
)


# ============================================================
# ADAPTADOR PARA POSTGRESQL
# ============================================================

class PostgresConnection:
    """
    Adaptador para que el resto de la aplicación pueda
    seguir utilizando conexion.execute(...) igual que SQLite.
    """

    def __init__(self, conexion):
        self.conexion = conexion

    def execute(self, sql, parametros=()):
        # La aplicación utiliza ? como marcador de parámetros.
        # PostgreSQL utiliza %s.
        sql = sql.replace("?", "%s")

        from psycopg2.extras import RealDictCursor

        cursor = self.conexion.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(sql, parametros)

        return cursor

    def commit(self):
        self.conexion.commit()

    def rollback(self):
        self.conexion.rollback()

    def close(self):
        self.conexion.close()


# ============================================================
# CONEXIÓN
# ============================================================

def conectar():
    """
    Conecta a PostgreSQL cuando DATABASE_URL existe.
    Si no existe, utiliza SQLite local.
    """

    if DATABASE_URL:
        import psycopg2

        conexion = psycopg2.connect(DATABASE_URL)

        return PostgresConnection(conexion)

    # SQLite local
    conexion = sqlite3.connect(DATABASE)

    conexion.row_factory = sqlite3.Row

    conexion.execute("PRAGMA foreign_keys = ON")

    return conexion


# ============================================================
# CONTEXTO DE BASE DE DATOS
# ============================================================

@contextmanager
def conexion_bd():
    """
    Entrega una conexión dentro de una transacción.

    Si todo funciona:
        COMMIT

    Si ocurre un error:
        ROLLBACK

    Finalmente:
        cierra la conexión.
    """

    conexion = conectar()

    try:
        yield conexion
        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


# ============================================================
# CREACIÓN DE BASE DE DATOS
# ============================================================

def crear_bd():
    """
    Crea las tablas necesarias.

    PostgreSQL:
        cuando existe DATABASE_URL.

    SQLite:
        cuando DATABASE_URL no existe.
    """

    if DATABASE_URL:
        crear_bd_postgresql()
    else:
        crear_bd_sqlite()


# ============================================================
# SQLITE
# ============================================================

def crear_bd_sqlite():

    conexion = sqlite3.connect(DATABASE)

    conexion.execute("PRAGMA foreign_keys = ON")

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

            FOREIGN KEY (id_barbero)
                REFERENCES barbero(id_barbero)
        );

        CREATE TABLE IF NOT EXISTS reserva (
            id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            id_barbero INTEGER NOT NULL,
            id_servicio INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Confirmada',

            FOREIGN KEY (id_cliente)
                REFERENCES cliente(id_cliente),

            FOREIGN KEY (id_barbero)
                REFERENCES barbero(id_barbero),

            FOREIGN KEY (id_servicio)
                REFERENCES servicio(id_servicio)
        );
    """)

    # Índices únicos
    indices = [
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_disponibilidad_unica
        ON disponibilidad (id_barbero, fecha, hora)
        """,

        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_reserva_confirmada_unica
        ON reserva (id_barbero, fecha, hora)
        WHERE estado = 'Confirmada'
        """
    ]

    for sentencia in indices:
        try:
            conexion.execute(sentencia)

        except sqlite3.IntegrityError:
            print(
                "AVISO: no se pudo crear un índice único "
                "porque existen registros duplicados."
            )

    conexion.commit()
    conexion.close()


# ============================================================
# POSTGRESQL / RENDER
# ============================================================

def crear_bd_postgresql():

    import psycopg2

    conexion = psycopg2.connect(DATABASE_URL)

    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cliente (
            id_cliente SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            correo TEXT
        );

        CREATE TABLE IF NOT EXISTS servicio (
            id_servicio SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            precio INTEGER NOT NULL,
            duracion INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS barbero (
            id_barbero SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS disponibilidad (
            id_disponibilidad SERIAL PRIMARY KEY,
            id_barbero INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            disponible INTEGER NOT NULL DEFAULT 1,

            FOREIGN KEY (id_barbero)
                REFERENCES barbero(id_barbero)
        );

        CREATE TABLE IF NOT EXISTS reserva (
            id_reserva SERIAL PRIMARY KEY,
            id_cliente INTEGER NOT NULL,
            id_barbero INTEGER NOT NULL,
            id_servicio INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Confirmada',

            FOREIGN KEY (id_cliente)
                REFERENCES cliente(id_cliente),

            FOREIGN KEY (id_barbero)
                REFERENCES barbero(id_barbero),

            FOREIGN KEY (id_servicio)
                REFERENCES servicio(id_servicio)
        );
    """)

    # Índice único para evitar horarios duplicados
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_disponibilidad_unica
        ON disponibilidad (id_barbero, fecha, hora)
    """)

    # Una sola reserva confirmada por barbero/fecha/hora
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_reserva_confirmada_unica
        ON reserva (id_barbero, fecha, hora)
        WHERE estado = 'Confirmada'
    """)

    conexion.commit()

    cursor.close()
    conexion.close()


# ============================================================
# EJECUCIÓN DIRECTA
# ============================================================

if __name__ == "__main__":

    crear_bd()

    if DATABASE_URL:
        print("Base de datos PostgreSQL creada correctamente.")
    else:
        print("Base de datos SQLite creada correctamente.")