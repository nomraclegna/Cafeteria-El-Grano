from datetime import datetime
from enum import StrEnum

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Unidad(StrEnum):
    GRAMOS = "g"
    MILILITROS = "ml"
    PIEZAS = "pieza"


class TipoMovimiento(StrEnum):
    ENTRADA = "entrada"
    VENTA = "venta"
    CANCELACION = "cancelacion"
    MERMA = "merma"


class Insumo(Base):
    __tablename__ = "insumos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60), unique=True)
    unidad: Mapped[Unidad]
    stock: Mapped[float] = mapped_column(Numeric(12, 2, asdecimal=False), default=0)
    stock_minimo: Mapped[float] = mapped_column(Numeric(12, 2, asdecimal=False), default=0)
    activo: Mapped[bool] = mapped_column(default=True)
    creado_en: Mapped[datetime] = mapped_column(default=datetime.now)

    @property
    def stock_bajo(self) -> bool:
        return self.stock <= self.stock_minimo


class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"

    id: Mapped[int] = mapped_column(primary_key=True)
    insumo_id: Mapped[int] = mapped_column(ForeignKey("insumos.id"), index=True)
    tipo: Mapped[TipoMovimiento]
    # Positiva cuando entra mercancía y negativa cuando sale
    cantidad: Mapped[float] = mapped_column(Numeric(12, 2, asdecimal=False))
    stock_resultante: Mapped[float] = mapped_column(Numeric(12, 2, asdecimal=False))
    motivo: Mapped[str | None] = mapped_column(String(200))
    pedido_id: Mapped[int | None] = mapped_column(ForeignKey("pedidos.id"), index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    fecha: Mapped[datetime] = mapped_column(default=datetime.now)

    insumo: Mapped[Insumo] = relationship(lazy="joined")
