from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CHAR,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.catalogos import Compania, MotivoNotaCredito, Tienda
from app.models.organizacion import Departamento
from app.models.usuarios import Usuario

MONEDAS = ("USD", "VES")
ESTADOS_NOTA = ("PENDIENTE", "PENDIENTE_SEGUNDA_FIRMA", "DEVUELTA", "APROBADA", "RECHAZADA")
ACCIONES_NOTA = ("CREAR", "APROBAR", "RECHAZAR", "DEVOLVER", "REENVIAR")


class NotaCredito(Base):
    __tablename__ = "notas_credito"
    __table_args__ = (
        CheckConstraint("monto > 0", name="monto_positivo"),
        CheckConstraint("moneda IN ('USD', 'VES')", name="moneda_valida"),
        CheckConstraint(
            "estado IN ('PENDIENTE', 'PENDIENTE_SEGUNDA_FIRMA', 'DEVUELTA', 'APROBADA', 'RECHAZADA')",
            name="estado_valido",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    departamento_id: Mapped[int] = mapped_column(ForeignKey("departamentos.id"), index=True)
    solicitante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    motivo_id: Mapped[int] = mapped_column(ForeignKey("motivos_nota_credito.id"), index=True)
    tienda_id: Mapped[int] = mapped_column(ForeignKey("tiendas.id"), index=True)
    compania_id: Mapped[int] = mapped_column(ForeignKey("companias.id"), index=True)
    factura_referencia: Mapped[str] = mapped_column(String(30))
    descripcion: Mapped[str] = mapped_column(Text)
    # Numeric y Decimal, nunca float: el dinero no admite errores de redondeo.
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    moneda: Mapped[str] = mapped_column(CHAR(3))
    estado: Mapped[str] = mapped_column(String(30), index=True)
    # Se guarda para que un cambio de umbral no altere las notas en curso.
    requiere_doble_aprobacion: Mapped[bool] = mapped_column(Boolean)
    primer_aprobador_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    creada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    departamento: Mapped[Departamento] = relationship()
    solicitante: Mapped[Usuario] = relationship(foreign_keys=[solicitante_id])
    primer_aprobador: Mapped[Usuario | None] = relationship(foreign_keys=[primer_aprobador_id])
    motivo: Mapped[MotivoNotaCredito] = relationship()
    tienda: Mapped[Tienda] = relationship()
    compania: Mapped[Compania] = relationship()
    eventos: Mapped[list["NotaCreditoEvento"]] = relationship(
        back_populates="nota",
        order_by=lambda: [NotaCreditoEvento.creado_en, NotaCreditoEvento.id],
    )


class NotaCreditoEvento(Base):
    # Auditoria de solo insercion: un trigger de PostgreSQL bloquea UPDATE y DELETE.
    __tablename__ = "notas_credito_eventos"
    __table_args__ = (
        CheckConstraint(
            "accion IN ('CREAR', 'APROBAR', 'RECHAZAR', 'DEVOLVER', 'REENVIAR')",
            name="accion_valida",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nota_id: Mapped[int] = mapped_column(ForeignKey("notas_credito.id"), index=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    accion: Mapped[str] = mapped_column(String(20))
    estado_anterior: Mapped[str | None] = mapped_column(String(30))
    estado_nuevo: Mapped[str] = mapped_column(String(30))
    comentario: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    nota: Mapped[NotaCredito] = relationship(back_populates="eventos")
    actor: Mapped[Usuario] = relationship()
