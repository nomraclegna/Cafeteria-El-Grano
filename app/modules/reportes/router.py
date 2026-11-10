from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import requiere_admin
from app.modules.inventario.schemas import InsumoOut
from app.modules.reportes.schemas import ProductoVendido, ReporteVentas
from app.modules.reportes.service import ReporteServicio

router = APIRouter(prefix="/reportes", tags=["6. Reportes"], dependencies=[Depends(requiere_admin)])

Servicio = Annotated[ReporteServicio, Depends()]


@router.get("/ventas", response_model=ReporteVentas)
def reporte_ventas(servicio: Servicio, fecha_inicio: date | None = None, fecha_fin: date | None = None):
    return servicio.ventas(fecha_inicio, fecha_fin)


@router.get("/productos-mas-vendidos", response_model=list[ProductoVendido])
def productos_mas_vendidos(
    servicio: Servicio,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    limite: Annotated[int, Query(ge=1, le=50)] = 5
):
    return servicio.productos_mas_vendidos(fecha_inicio, fecha_fin, limite)


@router.get("/stock-bajo", response_model=list[InsumoOut])
def insumos_con_stock_bajo(servicio: Servicio):
    return servicio.stock_bajo()
