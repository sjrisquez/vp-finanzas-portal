from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CHAR,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Departamento(Base):
    __tablename__ = "departamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(10), unique=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str | None] = mapped_column(Text)

    cargos: Mapped[list["Cargo"]] = relationship(back_populates="departamento")


class Nivel(Base):
    __tablename__ = "niveles"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True)
    orden: Mapped[int] = mapped_column(SmallInteger, unique=True)


# Tabla puente N:M: una funcion puede pertenecer a varios cargos.
cargo_funcion = Table(
    "cargo_funcion",
    Base.metadata,
    Column("cargo_id", ForeignKey("cargos.id", ondelete="CASCADE"), primary_key=True),
    Column("funcion_id", ForeignKey("funciones.id", ondelete="CASCADE"), primary_key=True),
)


class Cargo(Base):
    __tablename__ = "cargos"
    __table_args__ = (
        UniqueConstraint("nombre", "departamento_id", name="uq_cargos_nombre_departamento_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    departamento_id: Mapped[int] = mapped_column(ForeignKey("departamentos.id"), index=True)
    nivel_id: Mapped[int] = mapped_column(ForeignKey("niveles.id"), index=True)
    es_jefatura: Mapped[bool] = mapped_column(Boolean, server_default="false")

    departamento: Mapped[Departamento] = relationship(back_populates="cargos")
    nivel: Mapped[Nivel] = relationship()
    funciones: Mapped[list["Funcion"]] = relationship(secondary=cargo_funcion)


class Funcion(Base):
    __tablename__ = "funciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    descripcion: Mapped[str] = mapped_column(String(255), unique=True)


class Pais(Base):
    __tablename__ = "paises"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo_iso: Mapped[str] = mapped_column(CHAR(2), unique=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)


class Colaborador(Base):
    # No guarda departamento_id: el departamento se obtiene a traves del cargo.
    __tablename__ = "colaboradores"
    __table_args__ = (
        CheckConstraint("estado IN ('activo', 'inactivo')", name="estado_valido"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombres: Mapped[str] = mapped_column(String(80))
    apellidos: Mapped[str] = mapped_column(String(80))
    correo: Mapped[str] = mapped_column(String(150), unique=True)
    fecha_ingreso: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(10))
    pais_id: Mapped[int] = mapped_column(ForeignKey("paises.id"), index=True)
    cargo_id: Mapped[int] = mapped_column(ForeignKey("cargos.id"), index=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cargo: Mapped[Cargo] = relationship()
    pais: Mapped[Pais] = relationship()
