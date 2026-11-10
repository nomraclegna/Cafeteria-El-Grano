from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.pedidos.models import EstadoPedido, MetodoPago
from app.modules.productos.schemas import ProductoResumen
from app.modules.usuarios.schemas import UsuarioResumen


class ItemPedido(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    producto_id: int = Field(examples=[3])
    cantidad: int = Field(gt=0, le=50, examples=[2])
    notas: str | None = Field(
        default=None, max_length=100, examples=["Extra caliente, poca espuma"],
        description="Indicaciones del cliente para preparar el producto"
    )


class PedidoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    cliente: str | None = Field(default=None, max_length=60, examples=["Sofía"])
    metodo_pago: MetodoPago = Field(examples=["efectivo"])
    monto_recibido: float | None = Field(
        default=None, ge=0, examples=[200], description="Obligatorio cuando el pago es en efectivo"
    )
    items: list[ItemPedido] = Field(min_length=1)


class CambioEstado(BaseModel):
    estado: Literal["en_preparacion", "entregado"] = Field(examples=["en_preparacion"])


class CancelacionPedido(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    motivo: str = Field(min_length=3, max_length=200, examples=["El cliente se retiró"])


class DetalleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    producto: ProductoResumen
    cantidad: int
    notas: str | None
    precio_unitario: float
    subtotal: float


class PedidoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente: str | None
    estado: EstadoPedido
    metodo_pago: MetodoPago
    total: float
    monto_recibido: float
    cambio: float
    motivo_cancelacion: str | None
    fecha: datetime
    usuario: UsuarioResumen
    detalles: list[DetalleOut]
