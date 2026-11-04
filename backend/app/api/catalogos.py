from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Compania, MotivoNotaCredito, Tienda
from app.schemas.notas_credito import CatalogoSalida, CompaniaSalida, MotivoSalida
from app.security.deps import require_roles

router = APIRouter(
    prefix="/api/catalogos",
    tags=["catalogos"],
    dependencies=[Depends(require_roles("ADMIN", "JEFE_DEPARTAMENTO", "APROBADOR"))],
)


@router.get("/motivos", response_model=list[MotivoSalida])
def listar_motivos(db: Annotated[Session, Depends(get_db)]) -> list[MotivoNotaCredito]:
    return list(db.scalars(select(MotivoNotaCredito).order_by(MotivoNotaCredito.nombre)))


@router.get("/tiendas", response_model=list[CatalogoSalida])
def listar_tiendas(db: Annotated[Session, Depends(get_db)]) -> list[Tienda]:
    return list(db.scalars(select(Tienda).order_by(Tienda.nombre)))


@router.get("/companias", response_model=list[CompaniaSalida])
def listar_companias(db: Annotated[Session, Depends(get_db)]) -> list[Compania]:
    return list(db.scalars(select(Compania).order_by(Compania.nombre)))


@router.get("/umbrales", response_model=dict[str, Decimal])
def obtener_umbrales() -> dict[str, Decimal]:
    # El formulario avisa de la doble firma sin copiar la regla en el cliente.
    return {"USD": settings.nc_umbral_usd, "VES": settings.nc_umbral_ves}
