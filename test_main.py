import requests
import pytest
import time
from datetime import datetime

URL_BASE = "http://localhost:8000"


# ─────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────

@pytest.fixture
def contacto_creado():
    """Crea un contacto antes del test y lo elimina al terminar."""
    timestamp = int(time.time() * 1000)
    payload = {
        "nombre": "Fixture Usuario",
        "telefono": f"8{timestamp % 1000000000:09d}",
        "email": f"fixture{timestamp}@test.com"
    }
    response = requests.post(f"{URL_BASE}/v1/contactos/crear", json=payload)
    assert response.status_code == 201, f"No se pudo crear el contacto fixture: {response.text}"
    contacto = response.json()["items"]
    yield contacto
    # Limpieza — intenta eliminar aunque el test ya lo haya borrado
    requests.delete(f"{URL_BASE}/v1/contactos/{contacto['id_contacto']}")


@pytest.fixture
def telefono_duplicado_limpio():
    """Elimina el teléfono duplicado del test 23 antes de que corra."""
    # Borramos si ya existe de una corrida anterior
    response = requests.get(f"{URL_BASE}/v1/contactos?limit=1000&skip=0")
    if response.status_code == 202:
        items = response.json().get("items", [])
        for item in items:
            if item["telefono"] == "1276393856":
                requests.delete(f"{URL_BASE}/v1/contactos/{item['id_contacto']}")
    yield


# ─────────────────────────────────────────────
# TESTS
# ─────────────────────────────────────────────

# 0. GET 202 / Mensaje de bienvenida
def test_read_root():
    url = f"{URL_BASE}/"
    response = requests.get(url)
    assert response.status_code == 202
    payload = response.json()
    assert payload["message"] == "Api de la Agenda"
    datetime.strptime(payload["datatime"], "%d/%m/%Y %H:%M:%S")


# 1. GET 202 /v1/contactos?limit=10&skip=0 primeros 10 contactos
def test_get_contactos_limit_10_skip_0():
    url = f"{URL_BASE}/v1/contactos?limit=10&skip=0"
    response = requests.get(url)
    assert response.status_code == 202
    payload = response.json()
    assert payload["table"] == "contactos"
    assert payload["limit"] == 10
    assert payload["skip"] == 0
    assert payload["count"] == 10
    assert len(payload["items"]) == 10


# 2. GET 202 /v1/contactos?limit=10&skip=99999 — skip tan alto que no hay registros
def test_get_contactos_limit_10_skip_90():
    url = f"{URL_BASE}/v1/contactos?limit=10&skip=99999"
    response = requests.get(url)
    assert response.status_code == 202
    payload = response.json()
    assert payload["table"] == "contactos"
    assert payload["items"] == []
    assert payload["count"] == 0


# 3. GET 422 /v1/contactos?limit=-10&skip=0 Error en limit
def test_get_contactos_limit_negativo_skip_0():
    url = f"{URL_BASE}/v1/contactos?limit=-10&skip=0"
    response = requests.get(url)
    assert response.status_code == 422


# 4. GET 422 /v1/contactos?limit=10&skip=-10 Error en skip
def test_get_contactos_limit_10_skip_negativo():
    url = f"{URL_BASE}/v1/contactos?limit=10&skip=-10"
    response = requests.get(url)
    assert response.status_code == 422


# 5. GET 202 /v1/contactos?limit=0&skip=0 vacio
def test_get_contactos_limit_0_skip_0():
    url = f"{URL_BASE}/v1/contactos?limit=0&skip=0"
    response = requests.get(url)
    assert response.status_code == 202
    payload = response.json()
    assert payload["items"] == []
    assert payload["count"] == 0


# 6. GET 202 /v1/contactos?skip=0 Regresar los primeros 10 contactos por default
def test_get_contactos_skip_0():
    url = f"{URL_BASE}/v1/contactos?skip=0"
    response = requests.get(url)
    assert response.status_code == 202
    payload = response.json()
    assert payload["limit"] == 10
    assert payload["skip"] == 0
    assert payload["count"] == 10


# 7. GET 202 /v1/contactos?limit=10 Regresar los primeros 10 contactos por default
def test_get_contactos_limit_10():
    url = f"{URL_BASE}/v1/contactos?limit=10"
    response = requests.get(url)
    assert response.status_code == 202
    payload = response.json()
    assert payload["limit"] == 10
    assert payload["skip"] == 0
    assert payload["count"] == 10


# 8. GET 202 /v1/contactos Regresar los primeros 10 contactos por default
def test_get_contactos():
    url = f"{URL_BASE}/v1/contactos"
    response = requests.get(url)
    assert response.status_code == 202
    payload = response.json()
    assert payload["limit"] == 10
    assert payload["skip"] == 0
    assert payload["count"] == 10


# 9. GET 422 /v1/contactos?limit=x&skip=100 Mensaje de Error en limit
def test_get_contactos_limit_x_skip_100():
    url = f"{URL_BASE}/v1/contactos?limit=x&skip=100"
    response = requests.get(url)
    assert response.status_code == 422


# 10. GET 422 /v1/contactos?limit=10&skip=x Mensaje de Error en skip
def test_get_contactos_limit_10_skip_x():
    url = f"{URL_BASE}/v1/contactos?limit=10&skip=x"
    response = requests.get(url)
    assert response.status_code == 422


# 11. GET 202 /v1/contactos/{id_contacto} valido — usa fixture
def test_get_contacto_by_id_valido(contacto_creado):
    url = f"{URL_BASE}/v1/contactos/{contacto_creado['id_contacto']}"
    response = requests.get(url)
    assert response.status_code == 202
    payload = response.json()
    assert payload["table"] == "contactos"
    assert payload["items"]["id_contacto"] == contacto_creado["id_contacto"]


# 12. GET 404 /v1/contactos/{id_contacto} inexistente
def test_get_contacto_by_id_inexistente():
    url = f"{URL_BASE}/v1/contactos/99999"
    response = requests.get(url)
    assert response.status_code == 404


# 13. POST 201 /v1/contactos/crear valido
def test_post_contacto_crear_valido():
    timestamp = int(time.time() * 1000)
    payload = {
        "nombre": "Prueba Usuario",
        "telefono": f"9{timestamp % 1000000000:09d}",
        "email": f"prueba{timestamp}@test.com"
    }
    response = requests.post(f"{URL_BASE}/v1/contactos/crear", json=payload)
    assert response.status_code == 201
    created = response.json()["items"]
    assert created["nombre"] == payload["nombre"]
    # Limpieza
    requests.delete(f"{URL_BASE}/v1/contactos/{created['id_contacto']}")


# 14. POST 400 /v1/contactos/crear dato invalido
def test_post_contacto_crear_invalido():
    payload = {"nombre": "", "telefono": "", "email": "invalid"}
    response = requests.post(f"{URL_BASE}/v1/contactos/crear", json=payload)
    assert response.status_code == 400


# 15. PUT 202 /v1/contactos/{id_contacto} valido — usa fixture
def test_put_contacto_update_valido(contacto_creado):
    payload = {"nombre": "Actualizado"}
    response = requests.put(
        f"{URL_BASE}/v1/contactos/{contacto_creado['id_contacto']}", json=payload
    )
    assert response.status_code == 202
    result = response.json()["items"]
    assert result["nombre"] == "Actualizado"


# 16. PUT 404 /v1/contactos/{id_contacto} inexistente
def test_put_contacto_update_inexistente():
    payload = {"nombre": "Nada"}
    response = requests.put(f"{URL_BASE}/v1/contactos/99999", json=payload)
    assert response.status_code == 404


# 17. DELETE 202 /v1/contactos/{id_contacto} valido — usa fixture
def test_delete_contacto_valido(contacto_creado):
    response = requests.delete(
        f"{URL_BASE}/v1/contactos/{contacto_creado['id_contacto']}"
    )
    assert response.status_code == 202


# 18. DELETE 404 /v1/contactos/{id_contacto} inexistente
def test_delete_contacto_inexistente():
    response = requests.delete(f"{URL_BASE}/v1/contactos/99999")
    assert response.status_code == 404


# 19. GET 422 /v1/contactos?limit=1.5&skip=0 tipo de dato invalido
def test_get_contactos_limit_float_skip_0():
    url = f"{URL_BASE}/v1/contactos?limit=1.5&skip=0"
    response = requests.get(url)
    assert response.status_code == 422


# 20. GET 422 /v1/contactos?limit=10&skip=xyz tipo de dato invalido
def test_get_contactos_limit_10_skip_xyz():
    url = f"{URL_BASE}/v1/contactos?limit=10&skip=xyz"
    response = requests.get(url)
    assert response.status_code == 422


# 21. GET 422 /v1/contactos/abc id no numerico
def test_get_contacto_by_id_texto():
    url = f"{URL_BASE}/v1/contactos/abc"
    response = requests.get(url)
    assert response.status_code == 422


# 22. POST 400 /v1/contactos/crear con JSON invalido
def test_post_contacto_crear_json_invalido():
    body = "esto no es json"
    response = requests.post(
        f"{URL_BASE}/v1/contactos/crear",
        data=body,
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422 or response.status_code == 400


# 23. POST 400 /v1/contactos/crear tel duplicado — usa fixture de limpieza
def test_post_contacto_crear_telefono_duplicado(telefono_duplicado_limpio):
    payload1 = {"nombre": "Duplicado Uno", "telefono": "1276393856", "email": "dup1@test.com"}
    response1 = requests.post(f"{URL_BASE}/v1/contactos/crear", json=payload1)
    assert response1.status_code in [201, 400]

    payload2 = {"nombre": "Duplicado Dos", "telefono": "1276393856", "email": "dup2@test.com"}
    response2 = requests.post(f"{URL_BASE}/v1/contactos/crear", json=payload2)
    assert response2.status_code == 400


# 26. PUT 422 /v1/contactos/abc id invalido
def test_put_contacto_update_id_texto():
    payload = {"nombre": "Texto"}
    response = requests.put(f"{URL_BASE}/v1/contactos/abc", json=payload)
    assert response.status_code == 422

# 27. DELETE 422 /v1/contactos/abc id invalido
def test_delete_contacto_id_texto():
    response = requests.delete(f"{URL_BASE}/v1/contactos/abc")
    assert response.status_code == 422