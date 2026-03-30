import sqlite3
import os
import csv

def append_csv_to_db(csv_path="app/datos_agenda.csv", db_path="agenda.db"):
    """Anexa los datos de un CSV a la tabla contactos."""
    if not os.path.exists(csv_path):
        print(f"CSV no encontrado: {csv_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    inserted = 0
    skipped = 0
    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) < 4:
                skipped += 1
                continue
            _, nombre, telefono, email = row
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO contactos (nombre, telefono, email) VALUES (?, ?, ?)",
                    (nombre.strip(), telefono.strip(), email.strip())
                )
                if cursor.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"Error insertando fila {row}: {e}")
                skipped += 1

    conn.commit()
    conn.close()

    print(f"CSV procesado: {inserted} insertados, {skipped} omitidos")


def init_db():
    """Inicializa la base de datos si no existe"""
    db_path = "agenda.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contactos (
            id_contacto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(100) NOT NULL,
            telefono VARCHAR(100) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    append_csv_to_db("app/datos_agenda.csv", db_path)
    print("Base de datos inicializada y CSV anexado correctamente")

if __name__ == "__main__":
    init_db()
