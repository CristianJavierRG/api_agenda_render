from fastapi import FastAPI
from fastapi import HTTPException # Un manejador de errores
import sqlite3
from datetime import datetime
from typing import List
from pydantic import BaseModel
from fastapi.responses import JSONResponse # El otro manejador de errores

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

@app.get(
    "/",
    status_code=202,
    summary="Endpoint raiz",
    description="Bienvenido a la API de Agenda",
)
def get_root():
    return {
        "message": "Api de Agenda",
        "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

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
                    },
                ],
                "count": 100,
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

@app.get(
    "/v1/contactos",
    status_code=202,
    summary="Endpoint que regresa los contactos paginados",
    response_model=ContactosResponse,
    description="""Endpoint que regresa los contactos paginados,
    Utiliza los siguientes query params:
    limit:int -> Numero de registros a regresar
    skip:int -> Numero de registros a omitir
    """
)
async def get_contactos(limit: int = 10, skip: int = 0):
    if limit < 0 or skip < 0:
        raise HTTPException(
            status_code=422,
            detail="Los numeros negativos no son validos"
        )

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_contacto, nombre, telefono, email
            FROM contactos
            LIMIT ? OFFSET ?
        """, (limit, skip))

        rows = cursor.fetchall()

        conn.close()

        contactos = [dict(row) for row in rows]

        data = {
            "table": "contactos",
            "items": contactos,
            "count": len(contactos),
            "datetime": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            "message": "Datos consultados exitosamente",
            "limit": limit,
            "skip": skip
        }

        return JSONResponse(
            status_code=202,
            content=data
        )

    except Exception as e:

        print(f"Error al consultar los contactos: {e.args}")

        return JSONResponse(
            status_code=400,
            content={
                "table":"contactos",
                "items":[],
                "count":0,
                "datetime":datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "message":"Error al consultar la base de datos",
                "limit":limit,
                "skip":skip
            }
        )

@app.get(
    "/v1/contactos/{id_contacto}",
    summary="Buscar contacto por ID",
    response_model=Contacto,
    description="Endpoint que regresa un contacto por su id_contacto"
)
async def get_contacto_by_id(id_contacto: int = 0):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_contacto, nombre, telefono, email
            FROM contactos
            WHERE id_contacto = ?
        """, (id_contacto,))

        row = cursor.fetchone()
        conn.close()

        data = {
            "table": "contactos",
            "items": dict(row),
            "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "message": "Dato consultado exitosamente"
        }

        if id_contacto < 0:
            raise HTTPException(
        status_code=400,
        detail="Los numeros negativos no son validos"
        )

        return JSONResponse(
            status_code=202,
            content=data
        )
    
    except Exception as e:
        print(f"Error al consultar los contactos: {e.args}")
        return JSONResponse(
        status_code=400,
        content={
            "table":"contactos",
            "item":[],
            "datatime":datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "message": f"Error al consultar el contacto"
            }
    )

@app.post(
    "/v1/contactos/crear",
    summary="Crear nuevo contacto",
    response_model=Contacto,
    description="Endpoint para insertar un nuevo contacto en la base de datos"
)
async def create_contacto(contacto: ContactoCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contactos (nombre, telefono, email) VALUES (?, ?, ?)",
                       (contacto.nombre, contacto.telefono, contacto.email))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT id_contacto, nombre, telefono, email FROM contactos WHERE id_contacto = ?", (new_id,))
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
    except Exception as e:
        print(f"Error al insertar el contacto: {e.args}")
        return JSONResponse(
            status_code=400,
            content={
                "table": "contactos",
                "items": [],
                "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "message": "Error al insertar el contacto"
            }
        )

@app.put(
    "/v1/contactos/{id_contacto}",
    summary="Modificar contacto",
    response_model=Contacto,
    description="Endpoint para modificar un contacto en la base de datos"
)
async def update_contacto(id_contacto: int, contacto: ContactoUpdate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contactos WHERE id_contacto = ?", (id_contacto,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Contacto no encontrado")

        cursor.execute("""
            UPDATE contactos
            SET nombre = COALESCE(?, nombre),
                telefono = COALESCE(?, telefono),
                email = COALESCE(?, email)
            WHERE id_contacto = ?
        """, (contacto.nombre, contacto.telefono, contacto.email, id_contacto))
        conn.commit()

        cursor.execute("SELECT id_contacto, nombre, telefono, email FROM contactos WHERE id_contacto = ?", (id_contacto,))
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
    except Exception as e:
        print(f"Error al actualizar el contacto: {e.args}")
        return JSONResponse(
            status_code=400,
            content={
                "table": "contactos",
                "items": [],
                "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "message": "Error al actualizar el contacto"
            }
        )

@app.delete(
    "/v1/contactos/{id_contacto}",
    summary="Eliminar contacto",
    response_model=Contacto,
    description="Endpoint para eliminar un contacto en la base de datos"
)
async def delete_contacto(id_contacto: int):
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
    except Exception as e:
        print(f"Error al eliminar el contacto: {e.args}")
        return JSONResponse(
            status_code=400,
            content={
                "table": "contactos",
                "items": [],
                "datatime": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "message": "Error al eliminar el contacto"
            }
        )