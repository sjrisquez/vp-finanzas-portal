from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.main import app
from app.models import Usuario
from app.security.deps import NOMBRE_COOKIE
from app.security.tokens import ALGORITMO, crear_token
from tests.conftest import CLAVE_TEST


def login(client: TestClient, correo: str, password: str = CLAVE_TEST):
    return client.post("/api/auth/login", json={"correo": correo, "password": password})


# Test 1 del brief: login y mensaje generico
def test_login_correcto_fija_cookie_segura(client, usuarios):
    respuesta = login(client, "admin@vpfinanzas.test")

    assert respuesta.status_code == 200
    cookie = respuesta.headers["set-cookie"].lower()
    assert f"{NOMBRE_COOKIE}=" in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "path=/" in cookie


def test_login_devuelve_datos_sin_credenciales(client, usuarios):
    cuerpo = login(client, "jefetes@vpfinanzas.test").json()

    assert cuerpo["rol"] == "JEFE_DEPARTAMENTO"
    assert cuerpo["departamento"]["codigo"] == "TES"
    assert "notas-credito" in cuerpo["modulos"]
    assert "password_hash" not in cuerpo
    assert "token" not in cuerpo


def test_contrasena_incorrecta_e_inexistente_dan_mismo_error(client, usuarios):
    incorrecta = login(client, "admin@vpfinanzas.test", "clave-equivocada")
    inexistente = login(client, "nadie@vpfinanzas.test")

    assert incorrecta.status_code == inexistente.status_code == 401
    assert incorrecta.json() == inexistente.json()
    assert NOMBRE_COOKIE not in client.cookies


def test_login_ignora_mayusculas_del_correo(client, usuarios):
    assert login(client, " ADMIN@vpfinanzas.test ").status_code == 200


def test_login_registra_ultimo_login(client, usuarios, db: Session):
    assert usuarios["admin"].ultimo_login is None

    login(client, "admin@vpfinanzas.test")

    db.expire_all()
    assert db.get(Usuario, usuarios["admin"].id).ultimo_login is not None


def test_login_valida_la_entrada(client):
    assert client.post("/api/auth/login", json={"correo": "a@b.test"}).status_code == 422


# Test 2 del brief: inactivos y endpoints protegidos
def test_usuario_inactivo_no_inicia_sesion(client, usuarios):
    assert login(client, "usuarioinactivo@vpfinanzas.test").status_code == 401


def test_colaborador_inactivo_no_inicia_sesion(client, usuarios):
    assert login(client, "colabinactivo@vpfinanzas.test").status_code == 401


def test_endpoints_protegidos_sin_cookie_dan_401(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.post("/api/auth/logout").status_code == 401


# Sesion
def test_me_devuelve_el_usuario_de_la_cookie(iniciar_sesion):
    cliente = iniciar_sesion("colab_tes")

    cuerpo = cliente.get("/api/auth/me").json()

    assert cuerpo["correo"] == "colabtes@vpfinanzas.test"
    assert cuerpo["rol"] == "COLABORADOR"
    assert "notas-credito" not in cuerpo["modulos"]


def test_desactivar_usuario_quita_el_acceso_de_inmediato(iniciar_sesion, usuarios, db: Session):
    cliente = iniciar_sesion("admin")
    assert cliente.get("/api/auth/me").status_code == 200

    db.get(Usuario, usuarios["admin"].id).activo = False
    db.commit()

    assert cliente.get("/api/auth/me").status_code == 401


def test_el_rol_se_lee_de_la_bd_y_no_del_token(iniciar_sesion, usuarios, db: Session):
    cliente = iniciar_sesion("admin")

    db.get(Usuario, usuarios["admin"].id).rol = "COLABORADOR"
    db.commit()

    assert cliente.get("/api/auth/me").json()["rol"] == "COLABORADOR"


def test_logout_borra_la_cookie(iniciar_sesion):
    cliente = iniciar_sesion("admin")

    assert cliente.post("/api/auth/logout").status_code == 204
    assert cliente.get("/api/auth/me").status_code == 401


# Tokens rechazados
def test_token_alterado_da_401(client, usuarios):
    client.cookies.set(NOMBRE_COOKIE, crear_token(usuarios["admin"].id) + "x")
    assert client.get("/api/auth/me").status_code == 401


def test_token_expirado_da_401(client, usuarios):
    ahora = datetime.now(UTC)
    token = jwt.encode(
        {"sub": str(usuarios["admin"].id), "iat": ahora - timedelta(hours=2), "exp": ahora - timedelta(hours=1)},
        settings.jwt_secret,
        algorithm=ALGORITMO,
    )
    client.cookies.set(NOMBRE_COOKIE, token)
    assert client.get("/api/auth/me").status_code == 401


def test_token_firmado_con_otro_secreto_da_401(client, usuarios):
    ahora = datetime.now(UTC)
    token = jwt.encode(
        {"sub": str(usuarios["admin"].id), "iat": ahora, "exp": ahora + timedelta(hours=1)},
        "otro-secreto-de-mas-de-32-caracteres-para-la-prueba",
        algorithm=ALGORITMO,
    )
    client.cookies.set(NOMBRE_COOKIE, token)
    assert client.get("/api/auth/me").status_code == 401


def test_token_sin_firma_da_401(client, usuarios):
    token = jwt.encode({"sub": str(usuarios["admin"].id)}, key=None, algorithm="none")
    client.cookies.set(NOMBRE_COOKIE, token)
    assert client.get("/api/auth/me").status_code == 401


# Errores internos
def test_error_interno_no_revela_detalles():
    def falla():
        raise RuntimeError("detalle interno secreto")

    app.dependency_overrides[get_db] = falla
    try:
        with TestClient(app, raise_server_exceptions=False) as cliente:
            respuesta = cliente.post(
                "/api/auth/login", json={"correo": "a@vpfinanzas.test", "password": "x"}
            )
    finally:
        app.dependency_overrides.clear()

    assert respuesta.status_code == 500
    assert respuesta.json() == {"detail": "Error interno del servidor"}
