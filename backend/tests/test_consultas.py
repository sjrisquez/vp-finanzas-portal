import pytest
from sqlalchemy.orm import Session

from app.models import Colaborador, Funcion

CAMPOS_PUBLICOS = {"id", "nombres", "apellidos", "correo", "cargo"}


def correos(respuesta) -> set[str]:
    return {fila["correo"].split("@")[0] for fila in respuesta.json()}


def id_departamento(usuarios, clave: str) -> int:
    return usuarios[clave].colaborador.cargo.departamento_id


# Departamentos
@pytest.mark.parametrize(
    ("clave", "esperado"),
    [
        ("admin", {"TES", "CON", "CTR"}),
        ("aprobador", {"TES", "CON", "CTR"}),
        ("jefe_tes", {"TES"}),
        ("colab_con", {"CON"}),
    ],
)
def test_listar_departamentos_segun_alcance(iniciar_sesion, clave, esperado):
    cliente = iniciar_sesion(clave)

    respuesta = cliente.get("/api/departamentos")

    assert respuesta.status_code == 200
    assert {fila["codigo"] for fila in respuesta.json()} == esperado


def test_detalle_de_departamento_incluye_cargos(iniciar_sesion, usuarios):
    cliente = iniciar_sesion("admin")

    cuerpo = cliente.get(f"/api/departamentos/{id_departamento(usuarios, 'jefe_con')}").json()

    assert cuerpo["codigo"] == "CON"
    assert {cargo["nombre"] for cargo in cuerpo["cargos"]} == {"Gerente", "Analista"}


# Test 3 del brief: JEFE de Tesoreria recibe 404 en recursos de Contabilidad
def test_jefe_recibe_404_fuera_de_su_departamento(iniciar_sesion, usuarios):
    cliente = iniciar_sesion("jefe_tes")
    otro = usuarios["colab_con"].colaborador

    assert cliente.get(f"/api/colaboradores/{otro.id}").status_code == 404
    assert cliente.get(f"/api/cargos/{otro.cargo_id}").status_code == 404
    assert cliente.get(f"/api/departamentos/{otro.cargo.departamento_id}").status_code == 404


def test_jefe_accede_a_recursos_de_su_departamento(iniciar_sesion, usuarios):
    cliente = iniciar_sesion("jefe_tes")
    propio = usuarios["colab_tes"].colaborador

    assert cliente.get(f"/api/colaboradores/{propio.id}").status_code == 200
    assert cliente.get(f"/api/cargos/{propio.cargo_id}").status_code == 200
    assert cliente.get(f"/api/departamentos/{propio.cargo.departamento_id}").status_code == 200


@pytest.mark.parametrize("clave", ["admin", "aprobador"])
def test_alcance_global_accede_a_cualquier_recurso(iniciar_sesion, usuarios, clave):
    cliente = iniciar_sesion(clave)
    otro = usuarios["colab_con"].colaborador

    assert cliente.get(f"/api/colaboradores/{otro.id}").status_code == 200
    assert cliente.get(f"/api/cargos/{otro.cargo_id}").status_code == 200


# Test 4 del brief: vista limitada y ficha ajena del Colaborador
def test_colaborador_recibe_vista_limitada(iniciar_sesion):
    cliente = iniciar_sesion("colab_tes")

    filas = cliente.get("/api/colaboradores").json()

    assert filas
    for fila in filas:
        assert set(fila) == CAMPOS_PUBLICOS


def test_colaborador_recibe_404_en_ficha_ajena(iniciar_sesion, usuarios):
    cliente = iniciar_sesion("colab_tes")

    companero = usuarios["jefe_tes"].colaborador
    assert cliente.get(f"/api/colaboradores/{companero.id}").status_code == 404


def test_colaborador_ve_su_ficha_completa(iniciar_sesion, usuarios):
    cliente = iniciar_sesion("colab_tes")
    propio = usuarios["colab_tes"].colaborador

    cuerpo = cliente.get(f"/api/colaboradores/{propio.id}").json()

    assert cuerpo["fecha_ingreso"] == "2020-01-01"
    assert cuerpo["estado"] == "activo"
    assert cuerpo["pais"]["codigo_iso"] == "VE"
    assert cuerpo["cargo"]["departamento"]["codigo"] == "TES"


def test_colaborador_no_descubre_inactivos(iniciar_sesion):
    cliente = iniciar_sesion("colab_tes")

    assert "colabinactivo" not in correos(cliente.get("/api/colaboradores"))
    assert "colabinactivo" not in correos(cliente.get("/api/colaboradores?estado=inactivo"))


def test_colaborador_solo_ve_su_departamento(iniciar_sesion, usuarios):
    cliente = iniciar_sesion("colab_tes")

    otro_departamento = id_departamento(usuarios, "colab_con")

    assert "colabcon" not in correos(cliente.get("/api/colaboradores"))
    assert cliente.get(f"/api/colaboradores?departamento_id={otro_departamento}").json() == []


# Directorio
@pytest.mark.parametrize("clave", ["admin", "aprobador"])
def test_alcance_global_ve_todo_con_vista_completa(iniciar_sesion, clave):
    cliente = iniciar_sesion(clave)

    respuesta = cliente.get("/api/colaboradores")

    assert len(respuesta.json()) == 8
    assert "fecha_ingreso" in respuesta.json()[0]


def test_jefe_ve_su_departamento_con_vista_completa(iniciar_sesion):
    cliente = iniciar_sesion("jefe_tes")

    respuesta = cliente.get("/api/colaboradores")

    assert correos(respuesta) == {"admin", "jefetes", "colabtes", "usuarioinactivo", "colabinactivo"}
    assert "fecha_ingreso" in respuesta.json()[0]


def test_jefe_no_amplia_su_alcance_con_el_filtro(iniciar_sesion, usuarios):
    cliente = iniciar_sesion("jefe_tes")

    otro_departamento = id_departamento(usuarios, "colab_con")

    assert cliente.get(f"/api/colaboradores?departamento_id={otro_departamento}").json() == []


def test_filtros_del_directorio(iniciar_sesion, usuarios):
    cliente = iniciar_sesion("admin")

    departamento = id_departamento(usuarios, "colab_con")
    assert correos(cliente.get(f"/api/colaboradores?departamento_id={departamento}")) == {
        "jefecon",
        "colabcon",
    }
    assert correos(cliente.get("/api/colaboradores?estado=inactivo")) == {"colabinactivo"}
    assert correos(cliente.get("/api/colaboradores?q=APROBA")) == {"aprobador"}


def test_busqueda_trata_comodines_como_texto(iniciar_sesion):
    cliente = iniciar_sesion("admin")

    assert cliente.get("/api/colaboradores?q=%25").json() == []


def test_filtro_de_estado_invalido_da_422(iniciar_sesion):
    cliente = iniciar_sesion("admin")

    assert cliente.get("/api/colaboradores?estado=otro").status_code == 422


# Cargos
def test_ficha_de_cargo_incluye_nivel_y_funciones(iniciar_sesion, usuarios, db: Session):
    cargo = db.get(Colaborador, usuarios["colab_tes"].colaborador_id).cargo
    cargo.funciones.append(Funcion(descripcion="Conciliar cuentas bancarias"))
    db.commit()
    cliente = iniciar_sesion("colab_tes")

    cuerpo = cliente.get(f"/api/cargos/{cargo.id}").json()

    assert cuerpo["nivel"]["nombre"] == "Semi-senior"
    assert cuerpo["departamento"]["codigo"] == "TES"
    assert [funcion["descripcion"] for funcion in cuerpo["funciones"]] == [
        "Conciliar cuentas bancarias"
    ]


def test_colaborador_recibe_404_en_cargo_ajeno(iniciar_sesion, usuarios):
    cliente = iniciar_sesion("colab_tes")

    cargo_de_su_jefe = usuarios["jefe_tes"].colaborador.cargo_id

    assert cliente.get(f"/api/cargos/{cargo_de_su_jefe}").status_code == 404


def test_recurso_inexistente_da_404(iniciar_sesion):
    cliente = iniciar_sesion("admin")

    assert cliente.get("/api/colaboradores/999999").status_code == 404
    assert cliente.get("/api/cargos/999999").status_code == 404
    assert cliente.get("/api/departamentos/999999").status_code == 404


# Protecciones transversales
@pytest.mark.parametrize(
    "ruta",
    ["/api/departamentos", "/api/departamentos/1", "/api/colaboradores", "/api/colaboradores/1", "/api/cargos/1"],
)
def test_endpoints_de_consulta_sin_sesion_dan_401(client, ruta):
    assert client.get(ruta).status_code == 401


def test_me_incluye_ids_para_mi_perfil(iniciar_sesion, usuarios):
    cliente = iniciar_sesion("colab_tes")
    propio = usuarios["colab_tes"].colaborador

    cuerpo = cliente.get("/api/auth/me").json()

    assert cuerpo["colaborador_id"] == propio.id
    assert cuerpo["cargo_id"] == propio.cargo_id


def test_ninguna_respuesta_expone_credenciales(iniciar_sesion, usuarios):
    cliente = iniciar_sesion("admin")
    propio = usuarios["admin"].colaborador

    for ruta in ["/api/colaboradores", f"/api/colaboradores/{propio.id}", "/api/auth/me"]:
        assert "password" not in cliente.get(ruta).text
