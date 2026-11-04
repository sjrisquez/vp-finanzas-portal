"""Reglas de negocio de las notas de credito. Los routers solo validan entrada y responden.

Cada transicion ocurre en una transaccion: bloquea la fila, valida, actualiza el estado,
inserta el evento de auditoria y confirma. Si algo falla, no queda ningun cambio.
"""
from datetime import UTC, datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session, joinedload, selectinload

from app.config import settings
from app.models import (
    Compania,
    Departamento,
    MotivoNotaCredito,
    NotaCredito,
    NotaCreditoEvento,
    Tienda,
    Usuario,
)
from app.schemas.notas_credito import NotaCreditoCrear, NotaCreditoReenviar
from app.security.deps import aplicar_alcance_departamento, departamento_del_usuario

PENDIENTE = "PENDIENTE"
PENDIENTE_SEGUNDA_FIRMA = "PENDIENTE_SEGUNDA_FIRMA"
DEVUELTA = "DEVUELTA"
APROBADA = "APROBADA"
RECHAZADA = "RECHAZADA"

CREAR = "CREAR"
APROBAR = "APROBAR"
RECHAZAR = "RECHAZAR"
DEVOLVER = "DEVOLVER"
REENVIAR = "REENVIAR"

# Maquina de estados como datos: agregar un estado es agregar una entrada aqui.
TRANSICIONES: dict[str, dict[str, str]] = {
    PENDIENTE: {APROBAR: APROBADA, RECHAZAR: RECHAZADA, DEVOLVER: DEVUELTA},
    PENDIENTE_SEGUNDA_FIRMA: {APROBAR: APROBADA, RECHAZAR: RECHAZADA},
    DEVUELTA: {REENVIAR: PENDIENTE},
    APROBADA: {},
    RECHAZADA: {},
}

ROLES_SOLICITANTES = {"ADMIN", "JEFE_DEPARTAMENTO"}
ROLES_APROBADORES = {"ADMIN", "APROBADOR"}

OPCIONES_NOTA = (
    joinedload(NotaCredito.departamento),
    joinedload(NotaCredito.motivo),
    joinedload(NotaCredito.tienda),
    joinedload(NotaCredito.compania),
    joinedload(NotaCredito.solicitante).joinedload(Usuario.colaborador),
    joinedload(NotaCredito.primer_aprobador).joinedload(Usuario.colaborador),
)


def _error(codigo: int, mensaje: str) -> HTTPException:
    return HTTPException(codigo, detail=mensaje)


def requiere_doble_aprobacion(monto: Decimal, moneda: str) -> bool:
    umbrales = {"USD": settings.nc_umbral_usd, "VES": settings.nc_umbral_ves}
    return monto > umbrales[moneda]


def puede_firmar(nota: NotaCredito, actor: Usuario) -> bool:
    # Separacion de funciones: nadie firma lo que solicito ni firma dos veces.
    return (
        actor.rol in ROLES_APROBADORES
        and actor.id != nota.solicitante_id
        and actor.id != nota.primer_aprobador_id
    )


def acciones_disponibles(nota: NotaCredito, actor: Usuario) -> list[str]:
    """Le dice al frontend que botones mostrar. El backend vuelve a validar cada accion."""
    acciones = []
    for accion in TRANSICIONES[nota.estado]:
        permitida = actor.id == nota.solicitante_id if accion == REENVIAR else puede_firmar(nota, actor)
        if permitida:
            acciones.append(accion)
    return acciones


def _cargar_con_bloqueo(db: Session, nota_id: int, actor: Usuario) -> NotaCredito:
    # FOR UPDATE: si dos personas actuan a la vez, la segunda espera y ve el estado ya cambiado.
    # populate_existing obliga a usar la fila recien bloqueada y no una copia anterior en memoria.
    consulta = (
        select(NotaCredito)
        .where(NotaCredito.id == nota_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    consulta = aplicar_alcance_departamento(consulta, NotaCredito.departamento_id, actor)
    nota = db.scalar(consulta)
    if nota is None:
        raise _error(status.HTTP_404_NOT_FOUND, "Nota de crédito no encontrada")
    return nota


def _destino(nota: NotaCredito, accion: str) -> str:
    destino = TRANSICIONES[nota.estado].get(accion)
    if destino is None:
        raise _error(
            status.HTTP_409_CONFLICT,
            f"La acción {accion} no es válida para una nota en estado {nota.estado}",
        )
    return destino


def _verificar_firmante(nota: NotaCredito, actor: Usuario) -> None:
    if actor.rol not in ROLES_APROBADORES:
        raise _error(status.HTTP_403_FORBIDDEN, "Tu rol no puede firmar notas de crédito")
    if actor.id == nota.solicitante_id:
        raise _error(status.HTTP_403_FORBIDDEN, "No puedes firmar una nota que solicitaste")
    if actor.id == nota.primer_aprobador_id:
        raise _error(status.HTTP_403_FORBIDDEN, "La segunda firma debe ser de otra persona")


def _registrar_evento(
    db: Session,
    nota: NotaCredito,
    actor: Usuario,
    accion: str,
    estado_anterior: str | None,
    comentario: str | None,
    momento: datetime,
) -> None:
    db.add(
        NotaCreditoEvento(
            nota_id=nota.id,
            actor_id=actor.id,
            accion=accion,
            estado_anterior=estado_anterior,
            estado_nuevo=nota.estado,
            comentario=comentario,
            creado_en=momento,
        )
    )


def _cambiar_estado(
    db: Session,
    nota: NotaCredito,
    actor: Usuario,
    accion: str,
    destino: str,
    comentario: str | None,
    momento: datetime | None,
) -> NotaCredito:
    momento = momento or datetime.now(UTC)
    estado_anterior = nota.estado
    nota.estado = destino
    nota.actualizada_en = momento
    _registrar_evento(db, nota, actor, accion, estado_anterior, comentario, momento)
    db.commit()
    return nota


def _verificar_referencias(db: Session, datos: NotaCreditoCrear) -> None:
    referencias = (
        (Departamento, datos.departamento_id, "departamento"),
        (MotivoNotaCredito, datos.motivo_id, "motivo"),
        (Tienda, datos.tienda_id, "tienda"),
        (Compania, datos.compania_id, "compañía"),
    )
    for modelo, identificador, nombre in referencias:
        if db.get(modelo, identificador) is None:
            raise _error(status.HTTP_422_UNPROCESSABLE_ENTITY, f"El {nombre} indicado no existe")


def _reservar_identificador(db: Session, momento: datetime) -> tuple[int, str]:
    # La secuencia de PostgreSQL no repite valores, ni siquiera con peticiones simultaneas.
    nota_id = db.scalar(text("SELECT nextval(pg_get_serial_sequence('notas_credito', 'id'))"))
    return nota_id, f"NC-{momento.year}-{nota_id:04d}"


def crear_nota(
    db: Session,
    actor: Usuario,
    datos: NotaCreditoCrear,
    *,
    momento: datetime | None = None,
    comentario: str | None = None,
) -> NotaCredito:
    """momento y comentario solo los usa el seed; ningun endpoint los recibe."""
    if actor.rol not in ROLES_SOLICITANTES:
        raise _error(status.HTTP_403_FORBIDDEN, "Tu rol no puede crear notas de crédito")
    if actor.rol == "JEFE_DEPARTAMENTO" and datos.departamento_id != departamento_del_usuario(actor):
        raise _error(status.HTTP_403_FORBIDDEN, "Solo puedes crear notas para tu departamento")
    _verificar_referencias(db, datos)

    momento = momento or datetime.now(UTC)
    nota_id, codigo = _reservar_identificador(db, momento)
    nota = NotaCredito(
        id=nota_id,
        codigo=codigo,
        solicitante_id=actor.id,
        estado=PENDIENTE,
        requiere_doble_aprobacion=requiere_doble_aprobacion(datos.monto, datos.moneda),
        creada_en=momento,
        actualizada_en=momento,
        **datos.model_dump(),
    )
    db.add(nota)
    db.flush()
    _registrar_evento(db, nota, actor, CREAR, None, comentario, momento)
    db.commit()
    return nota


def aprobar_nota(
    db: Session,
    actor: Usuario,
    nota_id: int,
    comentario: str | None = None,
    *,
    momento: datetime | None = None,
) -> NotaCredito:
    nota = _cargar_con_bloqueo(db, nota_id, actor)
    destino = _destino(nota, APROBAR)
    _verificar_firmante(nota, actor)

    if nota.estado == PENDIENTE and nota.requiere_doble_aprobacion:
        destino = PENDIENTE_SEGUNDA_FIRMA
        nota.primer_aprobador_id = actor.id
    return _cambiar_estado(db, nota, actor, APROBAR, destino, comentario, momento)


def rechazar_nota(
    db: Session, actor: Usuario, nota_id: int, comentario: str, *, momento: datetime | None = None
) -> NotaCredito:
    nota = _cargar_con_bloqueo(db, nota_id, actor)
    destino = _destino(nota, RECHAZAR)
    _verificar_firmante(nota, actor)
    return _cambiar_estado(db, nota, actor, RECHAZAR, destino, comentario, momento)


def devolver_nota(
    db: Session, actor: Usuario, nota_id: int, comentario: str, *, momento: datetime | None = None
) -> NotaCredito:
    nota = _cargar_con_bloqueo(db, nota_id, actor)
    destino = _destino(nota, DEVOLVER)
    _verificar_firmante(nota, actor)
    return _cambiar_estado(db, nota, actor, DEVOLVER, destino, comentario, momento)


def reenviar_nota(
    db: Session,
    actor: Usuario,
    nota_id: int,
    datos: NotaCreditoReenviar,
    *,
    momento: datetime | None = None,
) -> NotaCredito:
    nota = _cargar_con_bloqueo(db, nota_id, actor)
    if actor.id != nota.solicitante_id:
        raise _error(status.HTTP_403_FORBIDDEN, "Solo el solicitante puede reenviar la nota")
    destino = _destino(nota, REENVIAR)
    if db.get(MotivoNotaCredito, datos.motivo_id) is None:
        raise _error(status.HTTP_422_UNPROCESSABLE_ENTITY, "El motivo indicado no existe")

    nota.motivo_id = datos.motivo_id
    nota.descripcion = datos.descripcion
    nota.monto = datos.monto
    # El monto pudo cambiar, asi que la regla de doble firma se recalcula.
    nota.requiere_doble_aprobacion = requiere_doble_aprobacion(datos.monto, nota.moneda)
    return _cambiar_estado(db, nota, actor, REENVIAR, destino, datos.comentario, momento)


def listar_notas(
    db: Session,
    actor: Usuario,
    estado: str | None = None,
    departamento_id: int | None = None,
    pendientes_de_mi_firma: bool = False,
) -> list[NotaCredito]:
    if pendientes_de_mi_firma and actor.rol not in ROLES_APROBADORES:
        return []

    consulta = select(NotaCredito).options(*OPCIONES_NOTA)
    consulta = aplicar_alcance_departamento(consulta, NotaCredito.departamento_id, actor)
    if estado is not None:
        consulta = consulta.where(NotaCredito.estado == estado)
    if departamento_id is not None:
        consulta = consulta.where(NotaCredito.departamento_id == departamento_id)
    if pendientes_de_mi_firma:
        consulta = consulta.where(
            NotaCredito.estado.in_([PENDIENTE, PENDIENTE_SEGUNDA_FIRMA]),
            NotaCredito.solicitante_id != actor.id,
            or_(
                NotaCredito.primer_aprobador_id.is_(None),
                NotaCredito.primer_aprobador_id != actor.id,
            ),
        )
    return list(db.scalars(consulta.order_by(NotaCredito.creada_en.desc(), NotaCredito.id.desc())))


def obtener_nota(db: Session, actor: Usuario, nota_id: int) -> NotaCredito:
    consulta = (
        select(NotaCredito)
        .where(NotaCredito.id == nota_id)
        .options(
            *OPCIONES_NOTA,
            selectinload(NotaCredito.eventos)
            .joinedload(NotaCreditoEvento.actor)
            .joinedload(Usuario.colaborador),
        )
        .execution_options(populate_existing=True)
    )
    consulta = aplicar_alcance_departamento(consulta, NotaCredito.departamento_id, actor)
    nota = db.scalar(consulta)
    if nota is None:
        raise _error(status.HTTP_404_NOT_FOUND, "Nota de crédito no encontrada")
    return nota
