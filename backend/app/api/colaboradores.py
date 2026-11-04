from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session, joinedload

from app.db import get_db
from app.models import Cargo, Colaborador
from app.schemas.organizacion import ColaboradorDetalle, ColaboradorPublico
from app.security.deps import UsuarioAutenticado, aplicar_alcance_departamento

router = APIRouter(prefix="/api/colaboradores", tags=["colaboradores"])

ROL_VISTA_LIMITADA = "COLABORADOR"


def consulta_colaboradores() -> Select[tuple[Colaborador]]:
    return (
        select(Colaborador)
        .join(Colaborador.cargo)
        .options(
            joinedload(Colaborador.pais),
            joinedload(Colaborador.cargo).joinedload(Cargo.departamento),
            joinedload(Colaborador.cargo).joinedload(Cargo.nivel),
        )
    )


def a_publico(colaborador: Colaborador) -> ColaboradorPublico:
    return ColaboradorPublico(
        id=colaborador.id,
        nombres=colaborador.nombres,
        apellidos=colaborador.apellidos,
        correo=colaborador.correo,
        cargo=colaborador.cargo.nombre,
    )


@router.get("", response_model=list[ColaboradorDetalle] | list[ColaboradorPublico])
def listar_colaboradores(
    usuario: UsuarioAutenticado,
    db: Annotated[Session, Depends(get_db)],
    departamento_id: int | None = None,
    estado: Literal["activo", "inactivo"] | None = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
) -> list[ColaboradorDetalle] | list[ColaboradorPublico]:
    vista_limitada = usuario.rol == ROL_VISTA_LIMITADA

    consulta = consulta_colaboradores().order_by(Colaborador.apellidos, Colaborador.nombres)
    consulta = aplicar_alcance_departamento(consulta, Cargo.departamento_id, usuario)

    if departamento_id is not None:
        consulta = consulta.where(Cargo.departamento_id == departamento_id)
    if vista_limitada:
        # Permitirle filtrar por estado revelaria un dato que su vista no incluye.
        consulta = consulta.where(Colaborador.estado == "activo")
    elif estado is not None:
        consulta = consulta.where(Colaborador.estado == estado)
    if q:
        # autoescape: % y _ se buscan como texto, no como comodines.
        consulta = consulta.where(
            or_(
                Colaborador.nombres.icontains(q, autoescape=True),
                Colaborador.apellidos.icontains(q, autoescape=True),
                Colaborador.correo.icontains(q, autoescape=True),
            )
        )

    colaboradores = db.scalars(consulta).all()
    if vista_limitada:
        return [a_publico(colaborador) for colaborador in colaboradores]
    return [ColaboradorDetalle.model_validate(colaborador) for colaborador in colaboradores]


@router.get("/{colaborador_id}", response_model=ColaboradorDetalle)
def obtener_colaborador(
    colaborador_id: int, usuario: UsuarioAutenticado, db: Annotated[Session, Depends(get_db)]
) -> Colaborador:
    consulta = consulta_colaboradores().where(Colaborador.id == colaborador_id)
    if usuario.rol == ROL_VISTA_LIMITADA:
        consulta = consulta.where(Colaborador.id == usuario.colaborador_id)
    else:
        consulta = aplicar_alcance_departamento(consulta, Cargo.departamento_id, usuario)

    colaborador = db.scalar(consulta)
    if colaborador is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Colaborador no encontrado")
    return colaborador
