# Importar todo aqui registra las 13 tablas en Base.metadata (lo necesita Alembic).
from app.models.catalogos import Compania, MotivoNotaCredito, Tienda
from app.models.notas_credito import ACCIONES_NOTA, ESTADOS_NOTA, MONEDAS, NotaCredito, NotaCreditoEvento
from app.models.organizacion import (
    Cargo,
    Colaborador,
    Departamento,
    Funcion,
    Nivel,
    Pais,
    cargo_funcion,
)
from app.models.usuarios import ROLES, Usuario

__all__ = [
    "ACCIONES_NOTA",
    "ESTADOS_NOTA",
    "MONEDAS",
    "ROLES",
    "Cargo",
    "Colaborador",
    "Compania",
    "Departamento",
    "Funcion",
    "MotivoNotaCredito",
    "Nivel",
    "NotaCredito",
    "NotaCreditoEvento",
    "Pais",
    "Tienda",
    "Usuario",
    "cargo_funcion",
]
