import sqlite3
import os

def init_db():
    """Inicializa la base de datos si no existe"""
    db_path = "agenda.db"
    
    # Solo inicializar si no existe la BD o no tiene la tabla
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar si la tabla ya existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contactos'")
    if cursor.fetchone() is None:
        # Crear la tabla
        cursor.execute("""
            DROP TABLE IF EXISTS contactos;
            CREATE TABLE contactos (
                id_contacto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre VARCHAR(100) NOT NULL,
                telefono VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL
            )
        """)
        conn.commit()
        print("Base de datos inicializada correctamente")
    else:
        print("Base de datos ya existe")
    
    conn.close()

if __name__ == "__main__":
    init_db()
