from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import SoloAdmin, requiere_admin
from app.modules.usuarios.schemas import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.modules.usuarios.service import UsuarioServicio

router = APIRouter(prefix="/usuarios", tags=["2. Usuarios"], dependencies=[Depends(requiere_admin)])

Servicio = Annotated[UsuarioServicio, Depends()]


@router.get("", response_model=list[UsuarioOut])
def listar_usuarios(servicio: Servicio):
    return servicio.listar()


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(usuario_id: int, servicio: Servicio):
    return servicio.obtener(usuario_id)


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCreate, servicio: Servicio):
    return servicio.crear(datos)


@router.put("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(usuario_id: int, datos: UsuarioUpdate, servicio: Servicio, admin: SoloAdmin):
    return servicio.actualizar(usuario_id, datos, admin)


@router.delete("/{usuario_id}", response_model=UsuarioOut)
def desactivar_usuario(usuario_id: int, servicio: Servicio, admin: SoloAdmin):
    return servicio.desactivar(usuario_id, admin)
