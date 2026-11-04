from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Cargo, Departamento
from app.schemas.organizacion import DepartamentoDetalle, DepartamentoSalida
from app.security.deps import UsuarioAutenticado, aplicar_alcance_departamento

router = APIRouter(prefix="/api/departamentos", tags=["departamentos"])


@router.get("", response_model=list[DepartamentoSalida])
def listar_departamentos(
    usuario: UsuarioAutenticado, db: Annotated[Session, Depends(get_db)]
) -> list[Departamento]:
    consulta = select(Departamento).order_by(Departamento.nombre)
    consulta = aplicar_alcance_departamento(consulta, Departamento.id, usuario)
    return list(db.scalars(consulta))


@router.get("/{departamento_id}", response_model=DepartamentoDetalle)
def obtener_departamento(
    departamento_id: int, usuario: UsuarioAutenticado, db: Annotated[Session, Depends(get_db)]
) -> Departamento:
    consulta = (
        select(Departamento)
        .where(Departamento.id == departamento_id)
        .options(selectinload(Departamento.cargos).joinedload(Cargo.nivel))
    )
    consulta = aplicar_alcance_departamento(consulta, Departamento.id, usuario)
    departamento = db.scalar(consulta)
    if departamento is None:
        # 404 y no 403: no se revela que el recurso existe.
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Departamento no encontrado")
    return departamento
