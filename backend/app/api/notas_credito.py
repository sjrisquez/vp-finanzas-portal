from typing import Annotated, Literal

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import NotaCredito, Usuario
from app.schemas.notas_credito import (
    AprobarEntrada,
    CatalogoSalida,
    ComentarioObligatorio,
    CompaniaSalida,
    DepartamentoNota,
    EventoSalida,
    MotivoSalida,
    NotaCreditoCrear,
    NotaCreditoDetalle,
    NotaCreditoReenviar,
    NotaCreditoResumen,
)
from app.security.deps import UsuarioAutenticado, require_roles
from app.services import notas_credito as servicio

router = APIRouter(prefix="/api/notas-credito", tags=["notas-credito"])

Db = Annotated[Session, Depends(get_db)]
Lector = Annotated[Usuario, Depends(require_roles("ADMIN", "JEFE_DEPARTAMENTO", "APROBADOR"))]
Solicitante = Annotated[Usuario, Depends(require_roles("ADMIN", "JEFE_DEPARTAMENTO"))]
Firmante = Annotated[Usuario, Depends(require_roles("ADMIN", "APROBADOR"))]
EstadoNota = Literal["PENDIENTE", "PENDIENTE_SEGUNDA_FIRMA", "DEVUELTA", "APROBADA", "RECHAZADA"]


def nombre_de(usuario: Usuario) -> str:
    return f"{usuario.colaborador.nombres} {usuario.colaborador.apellidos}"


def a_resumen(nota: NotaCredito) -> NotaCreditoResumen:
    return NotaCreditoResumen(
        id=nota.id,
        codigo=nota.codigo,
        departamento=DepartamentoNota.model_validate(nota.departamento),
        solicitante=nombre_de(nota.solicitante),
        motivo=MotivoSalida.model_validate(nota.motivo),
        tienda=CatalogoSalida.model_validate(nota.tienda),
        compania=CompaniaSalida.model_validate(nota.compania),
        factura_referencia=nota.factura_referencia,
        monto=nota.monto,
        moneda=nota.moneda,
        estado=nota.estado,
        requiere_doble_aprobacion=nota.requiere_doble_aprobacion,
        creada_en=nota.creada_en,
        actualizada_en=nota.actualizada_en,
    )


def a_detalle(db: Session, usuario: Usuario, nota_id: int) -> NotaCreditoDetalle:
    # Se vuelve a leer para devolver el estado confirmado y el historial completo.
    nota = servicio.obtener_nota(db, usuario, nota_id)
    return NotaCreditoDetalle(
        **a_resumen(nota).model_dump(),
        descripcion=nota.descripcion,
        primer_aprobador=nombre_de(nota.primer_aprobador) if nota.primer_aprobador else None,
        acciones_disponibles=servicio.acciones_disponibles(nota, usuario),
        eventos=[
            EventoSalida(
                id=evento.id,
                accion=evento.accion,
                estado_anterior=evento.estado_anterior,
                estado_nuevo=evento.estado_nuevo,
                comentario=evento.comentario,
                actor=nombre_de(evento.actor),
                creado_en=evento.creado_en,
            )
            for evento in nota.eventos
        ],
    )


@router.get("", response_model=list[NotaCreditoResumen])
def listar_notas(
    usuario: Lector,
    db: Db,
    estado: EstadoNota | None = None,
    departamento_id: int | None = None,
    pendientes_de_mi_firma: bool = False,
) -> list[NotaCreditoResumen]:
    notas = servicio.listar_notas(db, usuario, estado, departamento_id, pendientes_de_mi_firma)
    return [a_resumen(nota) for nota in notas]


@router.post("", response_model=NotaCreditoDetalle, status_code=status.HTTP_201_CREATED)
def crear_nota(entrada: NotaCreditoCrear, usuario: Solicitante, db: Db) -> NotaCreditoDetalle:
    nota = servicio.crear_nota(db, usuario, entrada)
    return a_detalle(db, usuario, nota.id)


@router.get("/{nota_id}", response_model=NotaCreditoDetalle)
def obtener_nota(nota_id: int, usuario: Lector, db: Db) -> NotaCreditoDetalle:
    return a_detalle(db, usuario, nota_id)


@router.post("/{nota_id}/aprobar", response_model=NotaCreditoDetalle)
def aprobar_nota(
    nota_id: int, usuario: Firmante, db: Db, entrada: AprobarEntrada | None = None
) -> NotaCreditoDetalle:
    comentario = entrada.comentario if entrada else None
    servicio.aprobar_nota(db, usuario, nota_id, comentario)
    return a_detalle(db, usuario, nota_id)


@router.post("/{nota_id}/rechazar", response_model=NotaCreditoDetalle)
def rechazar_nota(
    nota_id: int, entrada: ComentarioObligatorio, usuario: Firmante, db: Db
) -> NotaCreditoDetalle:
    servicio.rechazar_nota(db, usuario, nota_id, entrada.comentario)
    return a_detalle(db, usuario, nota_id)


@router.post("/{nota_id}/devolver", response_model=NotaCreditoDetalle)
def devolver_nota(
    nota_id: int, entrada: ComentarioObligatorio, usuario: Firmante, db: Db
) -> NotaCreditoDetalle:
    servicio.devolver_nota(db, usuario, nota_id, entrada.comentario)
    return a_detalle(db, usuario, nota_id)


@router.put("/{nota_id}/reenviar", response_model=NotaCreditoDetalle)
def reenviar_nota(
    nota_id: int, entrada: NotaCreditoReenviar, usuario: UsuarioAutenticado, db: Db
) -> NotaCreditoDetalle:
    servicio.reenviar_nota(db, usuario, nota_id, entrada)
    return a_detalle(db, usuario, nota_id)
