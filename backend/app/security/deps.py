from collections.abc import Callable
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import InstrumentedAttribute, Session, joinedload

from app.db import get_db
from app.models import ROLES, Cargo, Colaborador, Usuario
from app.security.tokens import leer_usuario_id

NOMBRE_COOKIE = "vpf_sesion"
ROLES_ALCANCE_GLOBAL = {"ADMIN", "APROBADOR"}


def consulta_usuario() -> Select[tuple[Usuario]]:
    return select(Usuario).options(
        joinedload(Usuario.colaborador)
        .joinedload(Colaborador.cargo)
        .joinedload(Cargo.departamento)
    )


def puede_acceder(usuario: Usuario) -> bool:
    return usuario.activo and usuario.colaborador.estado == "activo"


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str | None, Cookie(alias=NOMBRE_COOKIE)] = None,
) -> Usuario:
    no_autenticado = HTTPException(status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    if token is None:
        raise no_autenticado

    usuario_id = leer_usuario_id(token)
    if usuario_id is None:
        raise no_autenticado

    # El rol y el estado se leen de la BD en cada peticion, nunca del token:
    # desactivar a un usuario le quita el acceso de inmediato.
    usuario = db.scalar(consulta_usuario().where(Usuario.id == usuario_id))
    if usuario is None or not puede_acceder(usuario):
        raise no_autenticado
    return usuario


UsuarioAutenticado = Annotated[Usuario, Depends(get_current_user)]


def require_roles(*roles: str) -> Callable[[Usuario], Usuario]:
    desconocidos = set(roles) - set(ROLES)
    if desconocidos:
        raise ValueError(f"Roles desconocidos: {desconocidos}")

    def verificar_rol(usuario: UsuarioAutenticado) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="No tienes permiso para esta accion")
        return usuario

    return verificar_rol


def departamento_del_usuario(usuario: Usuario) -> int:
    return usuario.colaborador.cargo.departamento_id


def tiene_alcance_global(usuario: Usuario) -> bool:
    return usuario.rol in ROLES_ALCANCE_GLOBAL


def aplicar_alcance_departamento(
    consulta: Select, columna_departamento: InstrumentedAttribute[int], usuario: Usuario
) -> Select:
    """Agrega el WHERE por departamento: lo fuera de alcance nunca sale de la BD."""
    if tiene_alcance_global(usuario):
        return consulta
    return consulta.where(columna_departamento == departamento_del_usuario(usuario))
