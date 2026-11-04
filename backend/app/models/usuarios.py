from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.organizacion import Colaborador

ROLES = ("ADMIN", "JEFE_DEPARTAMENTO", "APROBADOR", "COLABORADOR")


class Usuario(Base):
    # Separado de colaboradores: no todo colaborador tiene acceso al portal.
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint(
            "rol IN ('ADMIN', 'JEFE_DEPARTAMENTO', 'APROBADOR', 'COLABORADOR')",
            name="rol_valido",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    colaborador_id: Mapped[int] = mapped_column(ForeignKey("colaboradores.id"), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[str] = mapped_column(String(20))
    activo: Mapped[bool] = mapped_column(Boolean, server_default="true")
    ultimo_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    colaborador: Mapped[Colaborador] = relationship()
