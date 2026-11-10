from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import UsuarioActual
from app.modules.auth.schemas import TokenOut
from app.modules.auth.service import AuthServicio
from app.modules.usuarios.schemas import UsuarioOut

router = APIRouter(prefix="/auth", tags=["1. Autenticación"])


@router.post("/login", response_model=TokenOut)
def iniciar_sesion(
    formulario: Annotated[OAuth2PasswordRequestForm, Depends()],
    servicio: Annotated[AuthServicio, Depends()]
):
    return servicio.iniciar_sesion(formulario.username, formulario.password)


@router.get("/me", response_model=UsuarioOut)
def perfil(usuario: UsuarioActual):
    return usuario
