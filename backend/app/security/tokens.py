from datetime import UTC, datetime, timedelta

import jwt

from app.config import settings

ALGORITMO = "HS256"


def crear_token(usuario_id: int) -> str:
    ahora = datetime.now(UTC)
    claims = {
        "sub": str(usuario_id),
        "iat": ahora,
        "exp": ahora + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(claims, settings.jwt_secret, algorithm=ALGORITMO)


def leer_usuario_id(token: str) -> int | None:
    """Devuelve el id del usuario, o None si el token no es valido o expiro."""
    try:
        # Fijar el algoritmo impide que el token elija como se verifica.
        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[ALGORITMO],
            options={"require": ["sub", "iat", "exp"]},
        )
        return int(claims["sub"])
    except (jwt.PyJWTError, ValueError):
        return None
