from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import obtener_usuario_actual, requiere_admin
from app.modules.productos.models import Categoria
from app.modules.productos.schemas import ProductoCreate, ProductoOut, ProductoUpdate
from app.modules.productos.service import ProductoServicio

router = APIRouter(prefix="/productos", tags=["3. Productos"], dependencies=[Depends(obtener_usuario_actual)])

Servicio = Annotated[ProductoServicio, Depends()]


@router.get("", response_model=list[ProductoOut])
def listar_productos(servicio: Servicio, categoria: Categoria | None = None, solo_activos: bool = True):
    return servicio.listar(categoria, solo_activos)


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: int, servicio: Servicio):
    return servicio.obtener(producto_id)


@router.post("", response_model=ProductoOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(requiere_admin)])
def crear_producto(datos: ProductoCreate, servicio: Servicio):
    return servicio.crear(datos)


@router.put("/{producto_id}", response_model=ProductoOut, dependencies=[Depends(requiere_admin)])
def actualizar_producto(producto_id: int, datos: ProductoUpdate, servicio: Servicio):
    return servicio.actualizar(producto_id, datos)


@router.delete("/{producto_id}", response_model=ProductoOut, dependencies=[Depends(requiere_admin)])
def desactivar_producto(producto_id: int, servicio: Servicio):
    return servicio.desactivar(producto_id)
