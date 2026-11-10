from datetime import datetime
from enum import StrEnum

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.modules.inventario.models import Insumo


class Categoria(StrEnum):
    BEBIDA_CALIENTE = "bebida_caliente"
    BEBIDA_FRIA = "bebida_fria"
    ALIMENTO = "alimento"
    POSTRE = "postre"


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(200))
    categoria: Mapped[Categoria]
    precio: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False))
    activo: Mapped[bool] = mapped_column(default=True)
    creado_en: Mapped[datetime] = mapped_column(default=datetime.now)

    receta: Mapped[list["RecetaInsumo"]] = relationship(
        back_populates="producto", cascade="all, delete-orphan", lazy="selectin"
    )


class RecetaInsumo(Base):
    __tablename__ = "recetas"

    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"), primary_key=True)
    insumo_id: Mapped[int] = mapped_column(ForeignKey("insumos.id"), primary_key=True)
    # Cantidad del insumo que se consume para preparar una unidad del producto
    cantidad: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False))

    producto: Mapped[Producto] = relationship(back_populates="receta")
    insumo: Mapped[Insumo] = relationship(lazy="joined")
