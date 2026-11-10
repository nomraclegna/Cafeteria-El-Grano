from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def _a_bytes(password: str) -> bytes:
    # bcrypt solo admite contraseñas de hasta 72 bytes
    return password.encode("utf-8")[:72]


def hashear_password(password: str) -> str:
    return bcrypt.hashpw(_a_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(_a_bytes(password), password_hash.encode("utf-8"))


def crear_token(usuario_id: int, rol: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.minutos_expiracion_token)
    datos = {"sub": str(usuario_id), "rol": rol, "exp": expira}
    return jwt.encode(datos, settings.secret_key, algorithm=settings.algoritmo_jwt)


def obtener_id_desde_token(token: str) -> int | None:
    try:
        datos = jwt.decode(token, settings.secret_key, algorithms=[settings.algoritmo_jwt])
        return int(datos["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None
