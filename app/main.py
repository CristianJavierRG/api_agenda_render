from fastapi import FastAPI, HTTPException
import sqlite3
from datetime import datetime
from typing import List
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()


def init_db():
    """Asegura que la base de datos y tabla existen"""
    conn = sqlite3.connect("agenda.db")
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


@app.on_event("startup")
def startup():
    """Inicializa la BD al iniciar la aplicación"""
    init_db()


def get_db_connection():
    conn = sqlite3.connect("agenda.db")
    conn.row_factory = sqlite3.Row
    return conn


# ─── Modelos ───────────────────────────────────────────────────────────────────

class Contacto(BaseModel):
    id_contacto: int
    nombre: str
    telefono: str
    email: str


class ContactosResponse(BaseModel):
    table: str
    items: List[Contacto]
    count: int
    datatime: str
    message: str
    limit: int
    skip: int

    class Config:
        json_schema_extra = {
            "example": {
                "table": "contactos",
                "items": [
                    {
                        "id_contacto": 1,
                        "nombre": "Juan Pérez",
                        "telefono": "5510000001",
                        "email": "juan.perez@email.com"
                    }
                ],
                "count": 1,
                "datatime": "12/02/2026 22:15:00",
                "message": "Datos consultados exitosamente",
                "limit": 10,
                "skip": 0
            }
        }


class ContactoCreate(BaseModel):
    nombre: str
    telefono: str
    email: str


class ContactoUpdate(BaseModel):
    nombre: str | None = None
    telefono: str | None = None
    email: str | None = None


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/", status_code=202, summary="Endpoint raiz")
def get_root():
    return {
        "message": "Api de la Agenda",
        "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }


@app.get(
    "/v1/contactos",
    status_code=202,
    summary="Contactos paginados",
    response_model=ContactosResponse,
)
async def get_contactos(limit: int = 10, skip: int = 0):
    if limit < 0 or skip < 0:
        raise HTTPException(status_code=422, detail="Los numeros negativos no son validos")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_contacto, nombre, telefono, email FROM contactos LIMIT ? OFFSET ?",
            (limit, skip)
        )
        rows = cursor.fetchall()
        conn.close()

        contactos = [dict(row) for row in rows]
        return JSONResponse(
            status_code=202,
            content={
                "table": "contactos",
                "items": contactos,
                "count": len(contactos),
                "datetime": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "message": "Datos consultados exitosamente",
                "limit": limit,
                "skip": skip
            }
        )

    except Exception as e:
        print(f"[ERROR get_contactos] {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "table": "contactos",
                "items": [],
                "count": 0,
                "datetime": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "message": f"Error al consultar la base de datos: {type(e).__name__}",
                "limit": limit,
                "skip": skip
            }
        )


@app.get(
    "/v1/contactos/{id_contacto}",
    summary="Buscar contacto por ID",
    response_model=Contacto,
)
async def get_contacto_by_id(id_contacto: int):
    if id_contacto < 0:
        raise HTTPException(status_code=422, detail="Los numeros negativos no son validos")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_contacto, nombre, telefono, email FROM contactos WHERE id_contacto = ?",
            (id_contacto,)
        )
        row = cursor.fetchone()
        conn.close()

        if row is None:
            raise HTTPException(status_code=404, detail="Contacto no encontrado")

        return JSONResponse(
            status_code=202,
            content={
                "table": "contactos",
                "items": dict(row),
                "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "message": "Dato consultado exitosamente"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR get_contacto_by_id] {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "table": "contactos",
                "items": [],
                "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "message": f"Error al consultar el contacto: {type(e).__name__}"
            }
        )


@app.post(
    "/v1/contactos/crear",
    summary="Crear nuevo contacto",
    response_model=Contacto,
)
async def create_contacto(contacto: ContactoCreate):
    # Validación: campos no pueden estar vacíos
    if not contacto.nombre.strip() or not contacto.telefono.strip() or not contacto.email.strip():
        return JSONResponse(
            status_code=400,
            content={
                "table": "contactos",
                "items": [],
                "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "message": "Campos obligatorios no deben estar vacíos"
            }
        )

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contactos (nombre, telefono, email) VALUES (?, ?, ?)",
            (contacto.nombre.strip(), contacto.telefono.strip(), contacto.email.strip())
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute(
            "SELECT id_contacto, nombre, telefono, email FROM contactos WHERE id_contacto = ?",
            (new_id,)
        )
        new_contact = cursor.fetchone()
        conn.close()

        return JSONResponse(
            status_code=201,
            content={
                "table": "contactos",
                "items": dict(new_contact),
                "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "message": "Contacto creado exitosamente"
            }
        )

    except sqlite3.IntegrityError as e:
        if conn:
            conn.close()
        print(f"[IntegrityError create_contacto] {e}")
        return JSONResponse(
            status_code=400,
            content={
                "table": "contactos",
                "items": [],
                "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "message": "Dato duplicado o inválido: " + str(e)
            }
        )
    except Exception as e:
        if conn:
            conn.close()
        # Captura IntegrityError si viene envuelto (por alguna razón de driver)
        if "UNIQUE" in str(e) or "IntegrityError" in type(e).__name__:
            return JSONResponse(
                status_code=400,
                content={
                    "table": "contactos",
                    "items": [],
                    "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "message": "Dato duplicado o inválido"
                }
            )
        print(f"[ERROR create_contacto] {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "table": "contactos",
                "items": [],
                "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "message": f"Error al insertar el contacto: {type(e).__name__}: {e}"
            }
        )


@app.put(
    "/v1/contactos/{id_contacto}",
    summary="Modificar contacto",
    response_model=Contacto,
)
async def update_contacto(id_contacto: int, contacto: ContactoUpdate):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contactos WHERE id_contacto = ?", (id_contacto,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Contacto no encontrado")

        cursor.execute(
            """UPDATE contactos
               SET nombre   = COALESCE(?, nombre),
                   telefono = COALESCE(?, telefono),
                   email    = COALESCE(?, email)
               WHERE id_contacto = ?""",
            (contacto.nombre, contacto.telefono, contacto.email, id_contacto)
        )
        conn.commit()

        cursor.execute(
            "SELECT id_contacto, nombre, telefono, email FROM contactos WHERE id_contacto = ?",
            (id_contacto,)
        )
        updated_contact = cursor.fetchone()
        conn.close()

        return JSONResponse(
            status_code=202,
            content={
                "table": "contactos",
                "items": dict(updated_contact),
                "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "message": "Contacto actualizado exitosamente"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.close()
        print(f"[ERROR update_contacto] {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "table": "contactos",
                "items": [],
                "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "message": f"Error al actualizar el contacto: {type(e).__name__}: {e}"
            }
        )


@app.delete(
    "/v1/contactos/{id_contacto}",
    summary="Eliminar contacto",
    response_model=Contacto,
)
async def delete_contacto(id_contacto: int):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contactos WHERE id_contacto = ?", (id_contacto,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Contacto no encontrado")

        cursor.execute("DELETE FROM contactos WHERE id_contacto = ?", (id_contacto,))
        conn.commit()
        conn.close()

        return JSONResponse(
            status_code=202,
            content={
                "table": "contactos",
                "items": [],
                "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "message": "Contacto eliminado exitosamente"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.close()
        print(f"[ERROR delete_contacto] {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "table": "contactos",
                "items": [],
                "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "message": f"Error al eliminar el contacto: {type(e).__name__}: {e}"
            }
        )