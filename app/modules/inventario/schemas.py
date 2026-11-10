from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.inventario.models import TipoMovimiento, Unidad


class InsumoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(min_length=2, max_length=60, examples=["Leche de almendra"])
    unidad: Unidad = Field(examples=["ml"])
    stock_inicial: float = Field(default=0, ge=0, examples=[5000])
    stock_minimo: float = Field(default=0, ge=0, examples=[1000])


class InsumoUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str | None = Field(default=None, min_length=2, max_length=60)
    stock_minimo: float | None = Field(default=None, ge=0)
    activo: bool | None = None


class InsumoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    unidad: Unidad
    stock: float
    stock_minimo: float
    stock_bajo: bool
    activo: bool


class InsumoResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    unidad: Unidad


class EntradaCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    cantidad: float = Field(gt=0, examples=[2000])
    motivo: str | None = Field(default=None, max_length=200, examples=["Compra a proveedor"])


class MermaCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    cantidad: float = Field(gt=0, examples=[250])
    motivo: str = Field(min_length=3, max_length=200, examples=["Leche caducada"])


class MovimientoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    insumo: InsumoResumen
    tipo: TipoMovimiento
    cantidad: float
    stock_resultante: float
    motivo: str | None
    pedido_id: int | None
    usuario_id: int
    fecha: datetime
