from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Cargo, Departamento, Usuario
from app.security.deps import (
    NOMBRE_COOKIE,
    aplicar_alcance_departamento,
    departamento_del_usuario,
    require_roles,
    tiene_alcance_global,
)
from app.security.tokens import crear_token
from tests.conftest import SesionTest


def nombres_visibles(db: Session, usuario: Usuario) -> set[str]:
    consulta = aplicar_alcance_departamento(
        select(Departamento.codigo), Departamento.id, usuario
    )
    return set(db.scalars(consulta))


@pytest.mark.parametrize("clave", ["admin", "aprobador"])
def test_admin_y_aprobador_tienen_alcance_global(db, usuarios, clave):
    assert tiene_alcance_global(usuarios[clave])
    assert nombres_visibles(db, usuarios[clave]) == {"TES", "CON", "CTR"}


@pytest.mark.parametrize(
    ("clave", "esperado"),
    [("jefe_tes", {"TES"}), ("jefe_con", {"CON"}), ("colab_tes", {"TES"}), ("colab_con", {"CON"})],
)
def test_jefe_y_colaborador_solo_ven_su_departamento(db, usuarios, clave, esperado):
    assert not tiene_alcance_global(usuarios[clave])
    assert nombres_visibles(db, usuarios[clave]) == esperado


def test_el_alcance_filtra_en_la_consulta_sql(usuarios):
    consulta = aplicar_alcance_departamento(select(Cargo.id), Cargo.departamento_id, usuarios["jefe_tes"])

    assert "WHERE cargos.departamento_id" in str(consulta)


def test_el_departamento_sale_del_cargo(usuarios):
    usuario = usuarios["jefe_con"]

    assert departamento_del_usuario(usuario) == usuario.colaborador.cargo.departamento_id
    assert usuario.colaborador.cargo.departamento.codigo == "CON"


def test_require_roles_rechaza_roles_desconocidos():
    with pytest.raises(ValueError):
        require_roles("SUPERADMIN")


@pytest.fixture()
def app_de_prueba(db: Session) -> TestClient:
    aplicacion = FastAPI()

    @aplicacion.get("/solo-aprobadores")
    def solo_aprobadores(_: Annotated[Usuario, Depends(require_roles("ADMIN", "APROBADOR"))]) -> dict:
        return {"ok": True}

    def get_db_test():
        with SesionTest() as sesion:
            yield sesion

    aplicacion.dependency_overrides[get_db] = get_db_test
    return TestClient(aplicacion)


@pytest.mark.parametrize(
    ("clave", "codigo"),
    [("admin", 200), ("aprobador", 200), ("jefe_tes", 403), ("colab_tes", 403)],
)
def test_require_roles_aplica_la_matriz(app_de_prueba, usuarios, clave, codigo):
    app_de_prueba.cookies.set(NOMBRE_COOKIE, crear_token(usuarios[clave].id))

    assert app_de_prueba.get("/solo-aprobadores").status_code == codigo


def test_require_roles_sin_sesion_da_401(app_de_prueba):
    assert app_de_prueba.get("/solo-aprobadores").status_code == 401
