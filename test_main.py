import requests
import pytest
import time
from datetime import datetime

URL_BASE = "http://localhost:8000"


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


# 2. GET 202 /v1/contactos?limit=10&skip=90 ultimos 10 contacto
def test_get_contactos_limit_10_skip_90():
    url = f"{URL_BASE}/v1/contactos?limit=10&skip=90"
    response = requests.get(url)
    assert response.status_code == 202
    payload = response.json()
    assert payload["table"] == "contactos"
    assert payload["items"] == []
    assert payload["count"] == 0


# 3. GET 400 /v1/contactos?limit=-10&skip=0 Error en limit
def test_get_contactos_limit_negativo_skip_0():
    url = f"{URL_BASE}/v1/contactos?limit=-10&skip=0"
    response = requests.get(url)
    assert response.status_code == 422


# 4. GET 400 /v1/contactos?limit=10&skip=-10 Error en skip
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


# 9. GET 400 /v1/contactos?limit=x&skip=100 Mensaje de Error en limit
def test_get_contactos_limit_x_skip_100():
    url = f"{URL_BASE}/v1/contactos?limit=x&skip=100"
    response = requests.get(url)
    assert response.status_code == 422


# 10. GET 400 /v1/contactos?limit=10&skip=x Mensaje de Error en skip
def test_get_contactos_limit_10_skip_x():
    url = f"{URL_BASE}/v1/contactos?limit=10&skip=x"
    response = requests.get(url)
    assert response.status_code == 422


# 11. GET 202 /v1/contactos/{id_contacto} valido
def test_get_contacto_by_id_valido():
    url = f"{URL_BASE}/v1/contactos/1"
    response = requests.get(url)
    assert response.status_code == 202
    payload = response.json()
    assert payload["table"] == "contactos"
    assert payload["items"]["id_contacto"] == 1


# 12. GET 404 /v1/contactos/{id_contacto} inexistente
def test_get_contacto_by_id_inexistente():
    url = f"{URL_BASE}/v1/contactos/99999"
    response = requests.get(url)
    assert response.status_code == 404


# 13. POST 201 /v1/contactos/crear valido
def test_post_contacto_crear_valido():
    timestamp = int(time.time())
    payload = {
        "nombre": "Prueba Usuario",
        "telefono": f"9{timestamp % 1000000000:09d}",
        "email": f"prueba{timestamp}@test.com"
    }
    response = requests.post(f"{URL_BASE}/v1/contactos/crear", json=payload)
    assert response.status_code == 201
    created = response.json()["items"]
    assert created["nombre"] == payload["nombre"]


# 14. POST 400 /v1/contactos/crear dato invalido
def test_post_contacto_crear_invalido():
    payload = {"nombre": "", "telefono": "", "email": "invalid"}
    response = requests.post(f"{URL_BASE}/v1/contactos/crear", json=payload)
    assert response.status_code == 400


# 15. PUT 202 /v1/contactos/{id_contacto} valido
def test_put_contacto_update_valido():
    payload = {"nombre": "Actualizado"}
    response = requests.put(f"{URL_BASE}/v1/contactos/1", json=payload)
    assert response.status_code == 202
    result = response.json()["items"]
    assert result["nombre"] == "Actualizado"


# 16. PUT 404 /v1/contactos/{id_contacto} inexistente
def test_put_contacto_update_inexistente():
    payload = {"nombre": "Nada"}
    response = requests.put(f"{URL_BASE}/v1/contactos/99999", json=payload)
    assert response.status_code == 404


# 17. DELETE 202 /v1/contactos/{id_contacto} valido
def test_delete_contacto_valido():
    response = requests.delete(f"{URL_BASE}/v1/contactos/1")
    assert response.status_code == 202


# 18. DELETE 404 /v1/contactos/{id_contacto} inexistente
def test_delete_contacto_inexistente():
    response = requests.delete(f"{URL_BASE}/v1/contactos/99999")
    assert response.status_code == 404
