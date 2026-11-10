from datetime import date

from pydantic import BaseModel

from app.modules.pedidos.models import MetodoPago


class VentasPorMetodo(BaseModel):
    pedidos: int
    total: float


class ReporteVentas(BaseModel):
    fecha_inicio: date | None
    fecha_fin: date | None
    numero_pedidos: int
    total_vendido: float
    ticket_promedio: float
    pedidos_cancelados: int
    por_metodo_pago: dict[MetodoPago, VentasPorMetodo]


class ProductoVendido(BaseModel):
    producto_id: int
    nombre: str
    unidades_vendidas: int
    importe: float
