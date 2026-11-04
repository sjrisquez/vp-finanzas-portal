from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Monto = Annotated[
    Decimal, Field(gt=0, le=Decimal("999999999.99"), max_digits=14, decimal_places=2)
]
TextoObligatorio = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
Comentario = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]


class NotaCreditoCrear(BaseModel):
    # extra="forbid": el cliente no puede enviar estado, solicitante ni otros campos internos.
    model_config = ConfigDict(extra="forbid")

    departamento_id: int
    motivo_id: int
    tienda_id: int
    compania_id: int
    factura_referencia: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]
    descripcion: TextoObligatorio
    monto: Monto
    moneda: Literal["USD", "VES"]


class NotaCreditoReenviar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    motivo_id: int
    descripcion: TextoObligatorio
    monto: Monto
    comentario: Comentario | None = None


class AprobarEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comentario: Comentario | None = None


class ComentarioObligatorio(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comentario: Comentario


class CatalogoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class MotivoSalida(CatalogoSalida):
    codigo: str


class CompaniaSalida(CatalogoSalida):
    rubro: str


class DepartamentoNota(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str


class NotaCreditoResumen(BaseModel):
    id: int
    codigo: str
    departamento: DepartamentoNota
    solicitante: str
    motivo: MotivoSalida
    tienda: CatalogoSalida
    compania: CompaniaSalida
    factura_referencia: str
    monto: Decimal
    moneda: str
    estado: str
    requiere_doble_aprobacion: bool
    creada_en: datetime
    actualizada_en: datetime


class EventoSalida(BaseModel):
    id: int
    accion: str
    estado_anterior: str | None
    estado_nuevo: str
    comentario: str | None
    actor: str
    creado_en: datetime


class NotaCreditoDetalle(NotaCreditoResumen):
    descripcion: str
    primer_aprobador: str | None
    acciones_disponibles: list[str]
    eventos: list[EventoSalida]
