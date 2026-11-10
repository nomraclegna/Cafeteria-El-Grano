from pydantic import BaseModel, ConfigDict, Field

from app.modules.inventario.schemas import InsumoResumen
from app.modules.productos.models import Categoria


class RecetaItem(BaseModel):
    insumo_id: int = Field(examples=[1])
    cantidad: float = Field(gt=0, examples=[18])


class ProductoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(min_length=2, max_length=60, examples=["Capuchino"])
    descripcion: str | None = Field(default=None, max_length=200, examples=["Espresso con leche espumada"])
    categoria: Categoria = Field(examples=["bebida_caliente"])
    precio: float = Field(ge=0, examples=[55.0], description="Se permite 0 para productos de cortesía")
    receta: list[RecetaItem] = Field(min_length=1, description="Insumos que se descuentan del inventario por cada unidad vendida")


class ProductoUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str | None = Field(default=None, min_length=2, max_length=60)
    descripcion: str | None = Field(default=None, max_length=200)
    categoria: Categoria | None = None
    precio: float | None = Field(default=None, ge=0)
    activo: bool | None = None
    receta: list[RecetaItem] | None = Field(default=None, min_length=1)


class RecetaItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    insumo: InsumoResumen
    cantidad: float


class ProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    categoria: Categoria
    precio: float
    activo: bool
    receta: list[RecetaItemOut]


class ProductoResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
