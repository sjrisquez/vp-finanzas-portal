from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db import get_db
from app.models import Cargo
from app.schemas.organizacion import CargoDetalle
from app.security.deps import UsuarioAutenticado, aplicar_alcance_departamento

router = APIRouter(prefix="/api/cargos", tags=["cargos"])


@router.get("/{cargo_id}", response_model=CargoDetalle)
def obtener_cargo(
    cargo_id: int, usuario: UsuarioAutenticado, db: Annotated[Session, Depends(get_db)]
) -> Cargo:
    consulta = (
        select(Cargo)
        .where(Cargo.id == cargo_id)
        .options(
            joinedload(Cargo.departamento),
            joinedload(Cargo.nivel),
            selectinload(Cargo.funciones),
        )
    )
    if usuario.rol == "COLABORADOR":
        consulta = consulta.where(Cargo.id == usuario.colaborador.cargo_id)
    else:
        consulta = aplicar_alcance_departamento(consulta, Cargo.departamento_id, usuario)

    cargo = db.scalar(consulta)
    if cargo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Cargo no encontrado")
    return cargo
