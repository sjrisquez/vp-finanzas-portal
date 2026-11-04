from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.organizacion import Pais


class MotivoNotaCredito(Base):
    __tablename__ = "motivos_nota_credito"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)


class Tienda(Base):
    __tablename__ = "tiendas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    pais_id: Mapped[int] = mapped_column(ForeignKey("paises.id"), index=True)

    pais: Mapped[Pais] = relationship()


class Compania(Base):
    __tablename__ = "companias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    rubro: Mapped[str] = mapped_column(String(50))
