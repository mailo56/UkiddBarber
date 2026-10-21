import sqlite3

DATABASE = "database.db"


def conectar():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    return conexion


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

    conexion.commit()
    conexion.close()


if __name__ == "__main__":
    crear_bd()
    print("Base de datos creada correctamente.")