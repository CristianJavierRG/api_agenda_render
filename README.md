# API de Agenda

Esta es una API RESTful construida con FastAPI para gestionar una agenda de contactos. Utiliza SQLite como base de datos para almacenar la información de los contactos.

# LINK para utilizar mi api key

**https://api-agenda-render.onrender.com**

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido para construir APIs con Python.
- **SQLite**: Base de datos relacional ligera y embebida.
- **Pydantic**: Para validación de datos y modelos.
- **Uvicorn**: Servidor ASGI para ejecutar la aplicación.

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/CristianJavierRG/api_agenda_render.git
   cd api_agenda_render
   ```

2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso Local

Para ejecutar la aplicación localmente:

```bash
fastapi run app/main.py
```

La API estará disponible en `http://localhost:8000`.

Puedes acceder a la documentación interactiva en `http://localhost:8000/docs`.

## Endpoints

### GET /
- **Descripción**: Endpoint raíz que devuelve un mensaje de bienvenida.
- **Respuesta**: JSON con mensaje y fecha/hora actual.

### GET /v1/contactos
- **Descripción**: Obtiene una lista paginada de contactos.
- **Parámetros de consulta**:
  - `limit` (int, opcional): Número de registros a devolver (por defecto 10).
  - `skip` (int, opcional): Número de registros a omitir (por defecto 0).
- **Respuesta**: JSON con la lista de contactos, conteo y metadatos.

### GET /v1/contactos/{id_contacto}
- **Descripción**: Obtiene un contacto específico por su ID.
- **Parámetros de ruta**:
  - `id_contacto` (int): ID del contacto.
- **Respuesta**: JSON con los detalles del contacto.

### POST /v1/contactos
- **Descripción**: Crea un nuevo contacto.
- **Cuerpo de la solicitud**: JSON con `nombre`, `telefono` y `email`.
- **Respuesta**: JSON con el ID del nuevo contacto creado.

### PUT /v1/contactos/{id_contacto}
- **Descripción**: Actualiza un contacto existente.
- **Parámetros de ruta**:
  - `id_contacto` (int): ID del contacto a actualizar.
- **Cuerpo de la solicitud**: JSON con campos opcionales `nombre`, `telefono` y `email`.
- **Respuesta**: JSON confirmando la actualización.

### DELETE /v1/contactos/{id_contacto}
- **Descripción**: Elimina un contacto por su ID.
- **Parámetros de ruta**:
  - `id_contacto` (int): ID del contacto a eliminar.
- **Respuesta**: JSON confirmando la eliminación.

## Docker

Para ejecutar la aplicación usando Docker:

1. Construye la imagen:
   ```bash
   docker build -t api-agenda .
   ```

2. Ejecuta el contenedor:
   ```bash
   docker run -p 80:80 api-agenda
   ```

La API estará disponible en `http://localhost:80`.

## Despliegue en Render

Este proyecto está configurado para desplegarse en Render. Para subir la API a Render:

1. Crea una cuenta en [Render](https://render.com/).
2. Conecta tu repositorio de GitHub.
3. Crea un nuevo servicio web.
4. Configura el comando de inicio: `fastapi run app/main.py --port $PORT` (Render asigna automáticamente el puerto).
5. Despliega la aplicación.

## Base de Datos

La aplicación utiliza SQLite con un archivo de base de datos llamado `agenda.db`. La base de datos se crea automáticamente al ejecutar la aplicación si no existe. Incluye una tabla `contactos` con los campos:
- `id_contacto` (INTEGER PRIMARY KEY)
- `nombre` (TEXT)
- `telefono` (TEXT)
- `email` (TEXT)

## Contribución

Si deseas contribuir al proyecto:
1. Haz un fork del repositorio.
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`).
3. Haz commit de tus cambios (`git commit -am 'Agrega nueva funcionalidad'`).
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.
