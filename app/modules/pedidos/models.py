from datetime import datetime
from enum import StrEnum

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.modules.productos.models import Producto
from app.modules.usuarios.models import Usuario


class EstadoPedido(StrEnum):
    PENDIENTE = "pendiente"
    EN_PREPARACION = "en_preparacion"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"


class MetodoPago(StrEnum):
    EFECTIVO = "efectivo"
    TARJETA = "tarjeta"


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente: Mapped[str | None] = mapped_column(String(60))
    estado: Mapped[EstadoPedido] = mapped_column(default=EstadoPedido.PENDIENTE, index=True)
    metodo_pago: Mapped[MetodoPago]
    total: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False))
    monto_recibido: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False))
    cambio: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False), default=0)
    motivo_cancelacion: Mapped[str | None] = mapped_column(String(200))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    fecha: Mapped[datetime] = mapped_column(default=datetime.now, index=True)

    usuario: Mapped[Usuario] = relationship(lazy="joined")
    detalles: Mapped[list["DetallePedido"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan", lazy="selectin"
    )


class DetallePedido(Base):
    __tablename__ = "detalles_pedido"

    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), index=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("productos.id"))
    cantidad: Mapped[int]
    notas: Mapped[str | None] = mapped_column(String(100))
    # Se guarda el precio del momento de la venta para que el historial no cambie si después se modifica el precio
    precio_unitario: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False))
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False))

    pedido: Mapped[Pedido] = relationship(back_populates="detalles")
    producto: Mapped[Producto] = relationship(lazy="joined")
