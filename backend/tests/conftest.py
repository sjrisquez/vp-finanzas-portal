from collections.abc import Callable, Iterator
from datetime import date
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Cargo, Colaborador, Departamento, Nivel, Pais, Usuario
from app.security.passwords import hash_password

BACKEND_DIR = Path(__file__).resolve().parents[1]
CLAVE_TEST = "clave-de-prueba"
HASH_TEST = hash_password(CLAVE_TEST)  # Una sola vez: bcrypt es lento a proposito.

# Estos tests vacian tablas: si la URL no apunta a una BD de test, se detienen.
if not (make_url(settings.test_database_url).database or "").endswith("_test"):
    raise RuntimeError("TEST_DATABASE_URL debe apuntar a una base cuyo nombre termine en _test")

engine_test = create_engine(settings.test_database_url)
SesionTest = sessionmaker(bind=engine_test, autoflush=False, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def esquema() -> Iterator[None]:
    # Usa la migracion real, para probar tambien sus restricciones y el trigger.
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    with engine_test.begin() as conexion:
        config.attributes["connection"] = conexion
        command.downgrade(config, "base")
        command.upgrade(config, "head")
    yield


@pytest.fixture()
def db(esquema: None) -> Iterator[Session]:
    tablas = ", ".join(tabla.name for tabla in Base.metadata.sorted_tables)
    with SesionTest() as sesion:
        sesion.execute(text(f"TRUNCATE {tablas} RESTART IDENTITY CASCADE"))
        sesion.commit()
        yield sesion


@pytest.fixture()
def usuarios(db: Session) -> dict[str, Usuario]:
    pais = Pais(codigo_iso="VE", nombre="Venezuela")
    jefe_nivel = Nivel(nombre="Gerente", orden=4)
    analista_nivel = Nivel(nombre="Semi-senior", orden=2)
    tes = Departamento(codigo="TES", nombre="Tesoreria")
    con = Departamento(codigo="CON", nombre="Contabilidad")
    ctr = Departamento(codigo="CTR", nombre="Contraloria")

    def cargo(departamento: Departamento, nombre: str, jefatura: bool = False) -> Cargo:
        nivel = jefe_nivel if jefatura else analista_nivel
        return Cargo(nombre=nombre, departamento=departamento, nivel=nivel, es_jefatura=jefatura)

    jefe_tes, analista_tes = cargo(tes, "Gerente", True), cargo(tes, "Analista")
    jefe_con, analista_con = cargo(con, "Gerente", True), cargo(con, "Analista")
    subgerente = cargo(ctr, "Subgerente")

    def usuario(
        clave: str, rol: str, puesto: Cargo, activo: bool = True, estado: str = "activo"
    ) -> Usuario:
        colaborador = Colaborador(
            nombres=clave,
            apellidos="Prueba",
            correo=f"{clave}@vpfinanzas.test",
            fecha_ingreso=date(2020, 1, 1),
            estado=estado,
            pais=pais,
            cargo=puesto,
        )
        return Usuario(colaborador=colaborador, password_hash=HASH_TEST, rol=rol, activo=activo)

    resultado = {
        "admin": usuario("admin", "ADMIN", analista_tes),
        "jefe_tes": usuario("jefetes", "JEFE_DEPARTAMENTO", jefe_tes),
        "jefe_con": usuario("jefecon", "JEFE_DEPARTAMENTO", jefe_con),
        "aprobador": usuario("aprobador", "APROBADOR", subgerente),
        "colab_tes": usuario("colabtes", "COLABORADOR", analista_tes),
        "colab_con": usuario("colabcon", "COLABORADOR", analista_con),
        "usuario_inactivo": usuario("usuarioinactivo", "COLABORADOR", analista_tes, activo=False),
        "colab_inactivo": usuario("colabinactivo", "COLABORADOR", analista_tes, estado="inactivo"),
    }
    db.add_all(resultado.values())
    db.commit()
    return resultado


@pytest.fixture()
def client(db: Session) -> Iterator[TestClient]:
    def get_db_test() -> Iterator[Session]:
        with SesionTest() as sesion:
            yield sesion

    app.dependency_overrides[get_db] = get_db_test
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()


@pytest.fixture()
def iniciar_sesion(client: TestClient, usuarios: dict[str, Usuario]) -> Callable[[str], TestClient]:
    def _iniciar(clave: str) -> TestClient:
        correo = usuarios[clave].colaborador.correo
        respuesta = client.post("/api/auth/login", json={"correo": correo, "password": CLAVE_TEST})
        assert respuesta.status_code == 200, respuesta.text
        return client

    return _iniciar
