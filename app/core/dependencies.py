from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.database import SesionDB
from app.core.security import obtener_id_desde_token
from app.modules.usuarios.models import Rol, Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/api/auth/login")


def obtener_usuario_actual(token: Annotated[str, Depends(oauth2_scheme)], db: SesionDB) -> Usuario:
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado. Inicia sesión nuevamente.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    usuario_id = obtener_id_desde_token(token)
    if usuario_id is None:
        raise error

    # El rol se toma de la base de datos para que los cambios de permisos apliquen de inmediato
    usuario = db.get(Usuario, usuario_id)
    if not usuario or not usuario.activo:
        raise error
    return usuario


UsuarioActual = Annotated[Usuario, Depends(obtener_usuario_actual)]


def requiere_admin(usuario: UsuarioActual) -> Usuario:
    if usuario.rol != Rol.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operación solo está permitida para administradores."
        )
    return usuario


SoloAdmin = Annotated[Usuario, Depends(requiere_admin)]
