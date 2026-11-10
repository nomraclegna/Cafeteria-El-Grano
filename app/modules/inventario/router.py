from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import SoloAdmin, obtener_usuario_actual, requiere_admin
from app.modules.inventario.models import TipoMovimiento
from app.modules.inventario.schemas import (
    EntradaCreate,
    InsumoCreate,
    InsumoOut,
    InsumoUpdate,
    MermaCreate,
    MovimientoOut,
)
from app.modules.inventario.service import InventarioServicio

router = APIRouter(prefix="/inventario", tags=["4. Inventario"], dependencies=[Depends(obtener_usuario_actual)])

Servicio = Annotated[InventarioServicio, Depends()]


@router.get("/insumos", response_model=list[InsumoOut])
def listar_insumos(servicio: Servicio, solo_activos: bool = True):
    return servicio.listar(solo_activos)


@router.get("/insumos/{insumo_id}", response_model=InsumoOut)
def obtener_insumo(insumo_id: int, servicio: Servicio):
    return servicio.obtener(insumo_id)


@router.post("/insumos", response_model=InsumoOut, status_code=status.HTTP_201_CREATED)
def crear_insumo(datos: InsumoCreate, servicio: Servicio, admin: SoloAdmin):
    return servicio.crear(datos, admin.id)


@router.put("/insumos/{insumo_id}", response_model=InsumoOut, dependencies=[Depends(requiere_admin)])
def actualizar_insumo(insumo_id: int, datos: InsumoUpdate, servicio: Servicio):
    return servicio.actualizar(insumo_id, datos)


@router.delete("/insumos/{insumo_id}", response_model=InsumoOut, dependencies=[Depends(requiere_admin)])
def desactivar_insumo(insumo_id: int, servicio: Servicio):
    return servicio.desactivar(insumo_id)


@router.post("/insumos/{insumo_id}/entradas", response_model=MovimientoOut, status_code=status.HTTP_201_CREATED)
def registrar_entrada(insumo_id: int, datos: EntradaCreate, servicio: Servicio, admin: SoloAdmin):
    return servicio.registrar_entrada(insumo_id, datos, admin.id)


@router.post("/insumos/{insumo_id}/mermas", response_model=MovimientoOut, status_code=status.HTTP_201_CREATED)
def registrar_merma(insumo_id: int, datos: MermaCreate, servicio: Servicio, admin: SoloAdmin):
    return servicio.registrar_merma(insumo_id, datos, admin.id)


@router.get("/movimientos", response_model=list[MovimientoOut], dependencies=[Depends(requiere_admin)])
def listar_movimientos(
    servicio: Servicio,
    insumo_id: int | None = None,
    tipo: TipoMovimiento | None = None,
    limite: Annotated[int, Query(ge=1, le=500)] = 100
):
    return servicio.listar_movimientos(insumo_id, tipo, limite)
