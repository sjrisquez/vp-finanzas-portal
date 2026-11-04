from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier

import pytest
from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.config import settings
from app.models import NotaCredito, NotaCreditoEvento, Usuario
from app.security.deps import consulta_usuario
from app.services import notas_credito as servicio
from tests.conftest import SesionTest

BAJO = "100.00"
ALTO = "999999.00"


@pytest.fixture()
def crear(iniciar_sesion, usuarios, catalogos):
    def _crear(clave="jefe_tes", monto=BAJO, moneda="USD", departamento_de=None):
        cliente = iniciar_sesion(clave)
        departamento = usuarios[departamento_de or clave].colaborador.cargo.departamento_id
        respuesta = cliente.post(
            "/api/notas-credito",
            json={
                "departamento_id": departamento,
                "motivo_id": catalogos["motivo"],
                "tienda_id": catalogos["tienda"],
                "compania_id": catalogos["compania"],
                "factura_referencia": "FAC-1",
                "descripcion": "Nota de prueba",
                "monto": monto,
                "moneda": moneda,
            },
        )
        assert respuesta.status_code == 201, respuesta.text
        return respuesta.json()

    return _crear


def cuerpo_nota(usuarios, catalogos, clave_departamento="jefe_tes"):
    return {
        "departamento_id": usuarios[clave_departamento].colaborador.cargo.departamento_id,
        "motivo_id": catalogos["motivo"],
        "tienda_id": catalogos["tienda"],
        "compania_id": catalogos["compania"],
        "factura_referencia": "FAC-2",
        "descripcion": "Nota de prueba",
        "monto": BAJO,
        "moneda": "USD",
    }


def accion(cliente, nota_id, nombre, comentario="Comentario de prueba"):
    return cliente.post(f"/api/notas-credito/{nota_id}/{nombre}", json={"comentario": comentario})


# Creacion
def test_jefe_crea_nota_para_su_departamento(crear):
    nota = crear()

    assert nota["estado"] == "PENDIENTE"
    assert nota["codigo"] == f"NC-{nota['creada_en'][:4]}-{nota['id']:04d}"
    assert nota["solicitante"] == "jefetes Prueba"
    assert nota["monto"] == "100.00"


def test_admin_crea_nota_para_cualquier_departamento(crear):
    assert crear("admin", departamento_de="jefe_con")["departamento"]["codigo"] == "CON"


# Test 5 del brief
@pytest.mark.parametrize("clave", ["colab_tes", "aprobador"])
def test_colaborador_y_aprobador_no_crean_notas(iniciar_sesion, usuarios, catalogos, clave):
    cliente = iniciar_sesion(clave)

    respuesta = cliente.post("/api/notas-credito", json=cuerpo_nota(usuarios, catalogos))

    assert respuesta.status_code == 403


# Test 6 del brief
def test_jefe_no_crea_nota_para_otro_departamento(iniciar_sesion, usuarios, catalogos):
    cliente = iniciar_sesion("jefe_tes")

    respuesta = cliente.post("/api/notas-credito", json=cuerpo_nota(usuarios, catalogos, "jefe_con"))

    assert respuesta.status_code == 403


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("monto", "0"),
        ("monto", "-5.00"),
        ("monto", "10.123"),
        ("monto", "1000000000.00"),
        ("moneda", "EUR"),
        ("descripcion", "   "),
        ("factura_referencia", "x" * 31),
        ("motivo_id", 999999),
        ("estado", "APROBADA"),
    ],
)
def test_creacion_valida_la_entrada(iniciar_sesion, usuarios, catalogos, campo, valor):
    cliente = iniciar_sesion("jefe_tes")
    cuerpo = cuerpo_nota(usuarios, catalogos) | {campo: valor}

    assert cliente.post("/api/notas-credito", json=cuerpo).status_code == 422


# Test 7 del brief
def test_jefe_no_ve_notas_de_otros_departamentos(crear, iniciar_sesion):
    nota = crear("jefe_con")
    cliente = iniciar_sesion("jefe_tes")

    assert cliente.get("/api/notas-credito").json() == []
    assert cliente.get(f"/api/notas-credito/{nota['id']}").status_code == 404
    assert accion(cliente, nota["id"], "rechazar").status_code == 403


@pytest.mark.parametrize("clave", ["admin", "aprobador"])
def test_alcance_global_ve_todas_las_notas(crear, iniciar_sesion, clave):
    crear("jefe_tes")
    crear("jefe_con")
    cliente = iniciar_sesion(clave)

    assert len(cliente.get("/api/notas-credito").json()) == 2


def test_colaborador_no_accede_al_modulo(crear, iniciar_sesion):
    nota = crear()
    cliente = iniciar_sesion("colab_tes")

    assert cliente.get("/api/notas-credito").status_code == 403
    assert cliente.get(f"/api/notas-credito/{nota['id']}").status_code == 403
    assert cliente.get("/api/catalogos/motivos").status_code == 403


def test_sin_sesion_da_401(client):
    assert client.get("/api/notas-credito").status_code == 401
    assert client.get("/api/catalogos/motivos").status_code == 401


# Test 8 del brief
def test_nadie_aprueba_su_propia_nota_ni_el_admin(crear, iniciar_sesion):
    nota = crear("admin", departamento_de="jefe_tes")
    cliente = iniciar_sesion("admin")

    assert cliente.post(f"/api/notas-credito/{nota['id']}/aprobar").status_code == 403
    assert accion(cliente, nota["id"], "rechazar").status_code == 403
    assert accion(cliente, nota["id"], "devolver").status_code == 403
    assert cliente.get(f"/api/notas-credito/{nota['id']}").json()["estado"] == "PENDIENTE"


def test_jefe_no_puede_firmar(crear, iniciar_sesion):
    nota = crear()
    cliente = iniciar_sesion("jefe_tes")

    assert cliente.post(f"/api/notas-credito/{nota['id']}/aprobar").status_code == 403


# Test 9 del brief
def test_nota_bajo_el_umbral_se_aprueba_con_una_firma(crear, iniciar_sesion):
    nota = crear()
    cliente = iniciar_sesion("aprobador")

    respuesta = cliente.post(f"/api/notas-credito/{nota['id']}/aprobar")

    assert respuesta.status_code == 200
    assert nota["requiere_doble_aprobacion"] is False
    assert respuesta.json()["estado"] == "APROBADA"


# Test 10 del brief
def test_nota_sobre_el_umbral_requiere_dos_personas(crear, iniciar_sesion):
    nota = crear(monto=ALTO)
    assert nota["requiere_doble_aprobacion"] is True

    cliente = iniciar_sesion("aprobador")
    primera = cliente.post(f"/api/notas-credito/{nota['id']}/aprobar")
    assert primera.json()["estado"] == "PENDIENTE_SEGUNDA_FIRMA"
    assert primera.json()["primer_aprobador"] == "aprobador Prueba"

    assert cliente.post(f"/api/notas-credito/{nota['id']}/aprobar").status_code == 403

    cliente = iniciar_sesion("aprobador2")
    segunda = cliente.post(f"/api/notas-credito/{nota['id']}/aprobar")
    assert segunda.status_code == 200
    assert segunda.json()["estado"] == "APROBADA"


def test_primer_aprobador_tampoco_rechaza_la_segunda_firma(crear, iniciar_sesion):
    nota = crear(monto=ALTO)
    cliente = iniciar_sesion("aprobador")
    cliente.post(f"/api/notas-credito/{nota['id']}/aprobar")

    assert accion(cliente, nota["id"], "rechazar").status_code == 403


def test_segunda_firma_puede_rechazar(crear, iniciar_sesion):
    nota = crear(monto=ALTO)
    iniciar_sesion("aprobador").post(f"/api/notas-credito/{nota['id']}/aprobar")

    respuesta = accion(iniciar_sesion("aprobador2"), nota["id"], "rechazar")

    assert respuesta.json()["estado"] == "RECHAZADA"


def test_umbral_es_por_moneda(crear, monkeypatch):
    monkeypatch.setattr(settings, "nc_umbral_usd", Decimal("5000.00"))
    monkeypatch.setattr(settings, "nc_umbral_ves", Decimal("100.00"))

    assert crear(monto="4000.00", moneda="USD")["requiere_doble_aprobacion"] is False
    assert crear(monto="4000.00", moneda="VES")["requiere_doble_aprobacion"] is True


def test_monto_igual_al_umbral_no_requiere_doble_firma(crear, monkeypatch):
    monkeypatch.setattr(settings, "nc_umbral_usd", Decimal("5000.00"))

    assert crear(monto="5000.00")["requiere_doble_aprobacion"] is False


def test_cambiar_el_umbral_no_altera_notas_en_curso(crear, iniciar_sesion, monkeypatch):
    nota = crear(monto=BAJO)
    monkeypatch.setattr(settings, "nc_umbral_usd", Decimal("1.00"))

    respuesta = iniciar_sesion("aprobador").post(f"/api/notas-credito/{nota['id']}/aprobar")

    assert respuesta.json()["estado"] == "APROBADA"


# Test 11 del brief
@pytest.mark.parametrize("nombre", ["rechazar", "devolver"])
@pytest.mark.parametrize("cuerpo", [{}, {"comentario": ""}, {"comentario": "   "}])
def test_rechazar_o_devolver_sin_comentario_da_422(crear, iniciar_sesion, nombre, cuerpo):
    nota = crear()
    cliente = iniciar_sesion("aprobador")

    respuesta = cliente.post(f"/api/notas-credito/{nota['id']}/{nombre}", json=cuerpo)

    assert respuesta.status_code == 422


# Test 12 del brief
def test_aprobar_una_rechazada_da_409(crear, iniciar_sesion):
    nota = crear()
    cliente = iniciar_sesion("aprobador")
    accion(cliente, nota["id"], "rechazar")

    assert cliente.post(f"/api/notas-credito/{nota['id']}/aprobar").status_code == 409


def test_devolver_en_segunda_firma_da_409(crear, iniciar_sesion):
    nota = crear(monto=ALTO)
    iniciar_sesion("aprobador").post(f"/api/notas-credito/{nota['id']}/aprobar")

    assert accion(iniciar_sesion("aprobador2"), nota["id"], "devolver").status_code == 409


def test_reenviar_una_pendiente_da_409(crear, iniciar_sesion, catalogos):
    nota = crear()
    cliente = iniciar_sesion("jefe_tes")

    respuesta = cliente.put(
        f"/api/notas-credito/{nota['id']}/reenviar",
        json={"motivo_id": catalogos["motivo"], "descripcion": "Corregida", "monto": BAJO},
    )

    assert respuesta.status_code == 409


# Test 13 del brief
def test_solicitante_reenvia_devuelta_y_recalcula_la_regla(crear, iniciar_sesion, catalogos):
    nota = crear()
    accion(iniciar_sesion("aprobador"), nota["id"], "devolver")
    cliente = iniciar_sesion("jefe_tes")

    respuesta = cliente.put(
        f"/api/notas-credito/{nota['id']}/reenviar",
        json={"motivo_id": catalogos["motivo2"], "descripcion": "Corregida", "monto": ALTO},
    )

    cuerpo = respuesta.json()
    assert respuesta.status_code == 200
    assert cuerpo["estado"] == "PENDIENTE"
    assert cuerpo["monto"] == ALTO
    assert cuerpo["descripcion"] == "Corregida"
    assert cuerpo["motivo"]["id"] == catalogos["motivo2"]
    assert cuerpo["requiere_doble_aprobacion"] is True


@pytest.mark.parametrize(("clave", "codigo"), [("jefe_tes", 403), ("aprobador", 403), ("jefe_con", 404)])
def test_solo_el_solicitante_reenvia(crear, iniciar_sesion, catalogos, clave, codigo):
    nota = crear("admin", departamento_de="jefe_tes")
    accion(iniciar_sesion("aprobador"), nota["id"], "devolver")
    cliente = iniciar_sesion(clave)

    respuesta = cliente.put(
        f"/api/notas-credito/{nota['id']}/reenviar",
        json={"motivo_id": catalogos["motivo"], "descripcion": "Corregida", "monto": BAJO},
    )

    assert respuesta.status_code == codigo


# Test 14 del brief
def test_cada_transicion_genera_exactamente_un_evento(crear, iniciar_sesion, catalogos, usuarios):
    nota = crear(monto=ALTO)
    accion(iniciar_sesion("aprobador"), nota["id"], "devolver", "Corregir")
    iniciar_sesion("jefe_tes").put(
        f"/api/notas-credito/{nota['id']}/reenviar",
        json={"motivo_id": catalogos["motivo"], "descripcion": "Corregida", "monto": ALTO},
    )
    iniciar_sesion("aprobador").post(f"/api/notas-credito/{nota['id']}/aprobar")
    final = iniciar_sesion("aprobador2").post(f"/api/notas-credito/{nota['id']}/aprobar").json()

    eventos = [
        (e["accion"], e["estado_anterior"], e["estado_nuevo"], e["actor"]) for e in final["eventos"]
    ]
    assert eventos == [
        ("CREAR", None, "PENDIENTE", "jefetes Prueba"),
        ("DEVOLVER", "PENDIENTE", "DEVUELTA", "aprobador Prueba"),
        ("REENVIAR", "DEVUELTA", "PENDIENTE", "jefetes Prueba"),
        ("APROBAR", "PENDIENTE", "PENDIENTE_SEGUNDA_FIRMA", "aprobador Prueba"),
        ("APROBAR", "PENDIENTE_SEGUNDA_FIRMA", "APROBADA", "auditora Prueba"),
    ]
    assert final["eventos"][1]["comentario"] == "Corregir"
    assert all(evento["creado_en"] for evento in final["eventos"])


def test_accion_rechazada_no_genera_evento(crear, iniciar_sesion):
    nota = crear()
    cliente = iniciar_sesion("jefe_tes")
    cliente.post(f"/api/notas-credito/{nota['id']}/aprobar")

    assert len(cliente.get(f"/api/notas-credito/{nota['id']}").json()["eventos"]) == 1


def test_trigger_impide_modificar_la_auditoria(crear, db: Session):
    crear()

    with pytest.raises(DBAPIError, match="solo insercion"):
        db.execute(text("UPDATE notas_credito_eventos SET comentario = 'alterado'"))
    db.rollback()

    with pytest.raises(DBAPIError, match="solo insercion"):
        db.execute(text("DELETE FROM notas_credito_eventos"))
    db.rollback()


# Concurrencia
def test_dos_aprobadores_simultaneos_generan_una_sola_aprobacion(crear, usuarios, db: Session):
    nota_id = crear()["id"]
    barrera = Barrier(2)

    def aprobar(usuario_id: int) -> int:
        with SesionTest() as sesion:
            actor = sesion.scalar(consulta_usuario().where(Usuario.id == usuario_id))
            barrera.wait()
            try:
                servicio.aprobar_nota(sesion, actor, nota_id)
                return 200
            except HTTPException as error:
                return error.status_code

    ids = [usuarios["aprobador"].id, usuarios["aprobador2"].id]
    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        codigos = sorted(ejecutor.map(aprobar, ids))

    assert codigos == [200, 409]
    db.expire_all()
    assert db.get(NotaCredito, nota_id).estado == "APROBADA"
    eventos = db.scalars(select(NotaCreditoEvento).where(NotaCreditoEvento.nota_id == nota_id)).all()
    assert [evento.accion for evento in eventos] == ["CREAR", "APROBAR"]


# Bandeja y acciones disponibles
def test_filtro_por_estado(crear, iniciar_sesion):
    nota = crear()
    crear()
    accion(iniciar_sesion("aprobador"), nota["id"], "rechazar")
    cliente = iniciar_sesion("admin")

    filas = cliente.get("/api/notas-credito?estado=RECHAZADA").json()

    assert [fila["id"] for fila in filas] == [nota["id"]]
    assert cliente.get("/api/notas-credito?estado=OTRO").status_code == 422


def test_pendientes_de_mi_firma(crear, iniciar_sesion):
    propia = crear("admin", departamento_de="jefe_tes")
    firmada = crear(monto=ALTO)
    pendiente = crear()
    iniciar_sesion("aprobador").post(f"/api/notas-credito/{firmada['id']}/aprobar")

    def pendientes(clave):
        filas = iniciar_sesion(clave).get("/api/notas-credito?pendientes_de_mi_firma=true").json()
        return {fila["id"] for fila in filas}

    assert pendientes("aprobador") == {propia["id"], pendiente["id"]}
    assert pendientes("aprobador2") == {propia["id"], firmada["id"], pendiente["id"]}
    assert pendientes("admin") == {firmada["id"], pendiente["id"]}
    assert pendientes("jefe_tes") == set()


def test_acciones_disponibles_segun_estado_y_usuario(crear, iniciar_sesion):
    nota = crear()
    ruta = f"/api/notas-credito/{nota['id']}"

    assert nota["acciones_disponibles"] == []
    cliente = iniciar_sesion("aprobador")
    assert cliente.get(ruta).json()["acciones_disponibles"] == ["APROBAR", "RECHAZAR", "DEVOLVER"]

    accion(cliente, nota["id"], "devolver")
    assert cliente.get(ruta).json()["acciones_disponibles"] == []
    assert iniciar_sesion("jefe_tes").get(ruta).json()["acciones_disponibles"] == ["REENVIAR"]


def test_catalogos_para_el_formulario(iniciar_sesion, catalogos):
    cliente = iniciar_sesion("jefe_tes")

    assert len(cliente.get("/api/catalogos/motivos").json()) == 2
    assert cliente.get("/api/catalogos/tiendas").json()[0]["nombre"] == "Tienda de prueba"
    assert cliente.get("/api/catalogos/companias").json()[0]["rubro"] == "Farmaceutico"


def test_umbrales_para_el_aviso_del_formulario(iniciar_sesion):
    cuerpo = iniciar_sesion("jefe_tes").get("/api/catalogos/umbrales").json()

    assert Decimal(cuerpo["USD"]) == settings.nc_umbral_usd
    assert Decimal(cuerpo["VES"]) == settings.nc_umbral_ves
