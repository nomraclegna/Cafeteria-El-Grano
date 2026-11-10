from datetime import date

from sqlalchemy import func, select

from app.core.database import SesionDB
from app.core.exceptions import ReglaNegocioError
from app.modules.inventario.models import Insumo
from app.modules.inventario.repository import InsumoRepositorio
from app.modules.pedidos.models import DetallePedido, EstadoPedido, MetodoPago, Pedido
from app.modules.pedidos.repository import rango_de_fechas
from app.modules.productos.models import Producto
from app.modules.reportes.schemas import ProductoVendido, ReporteVentas, VentasPorMetodo


class ReporteServicio:
    def __init__(self, db: SesionDB):
        self.db = db
        self.insumos = InsumoRepositorio(db)

    def ventas(self, fecha_inicio: date | None, fecha_fin: date | None) -> ReporteVentas:
        condiciones = self._condiciones(fecha_inicio, fecha_fin)

        filas = self.db.execute(
            select(Pedido.metodo_pago, func.count(Pedido.id), func.sum(Pedido.total))
            .where(*condiciones, Pedido.estado != EstadoPedido.CANCELADO)
            .group_by(Pedido.metodo_pago)
        ).all()

        por_metodo = {metodo: VentasPorMetodo(pedidos=0, total=0) for metodo in MetodoPago}
        for metodo, pedidos, total in filas:
            por_metodo[metodo] = VentasPorMetodo(pedidos=pedidos, total=round(total, 2))

        numero_pedidos = sum(v.pedidos for v in por_metodo.values())
        total_vendido = round(sum(v.total for v in por_metodo.values()), 2)
        cancelados = self.db.scalar(
            select(func.count(Pedido.id)).where(*condiciones, Pedido.estado == EstadoPedido.CANCELADO)
        )

        return ReporteVentas(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            numero_pedidos=numero_pedidos,
            total_vendido=total_vendido,
            ticket_promedio=round(total_vendido / numero_pedidos, 2) if numero_pedidos else 0,
            pedidos_cancelados=cancelados,
            por_metodo_pago=por_metodo
        )

    def productos_mas_vendidos(
        self, fecha_inicio: date | None, fecha_fin: date | None, limite: int
    ) -> list[ProductoVendido]:
        unidades = func.sum(DetallePedido.cantidad).label("unidades")
        filas = self.db.execute(
            select(Producto.id, Producto.nombre, unidades, func.sum(DetallePedido.subtotal))
            .select_from(DetallePedido)
            .join(Producto, DetallePedido.producto_id == Producto.id)
            .join(Pedido, DetallePedido.pedido_id == Pedido.id)
            .where(*self._condiciones(fecha_inicio, fecha_fin), Pedido.estado != EstadoPedido.CANCELADO)
            .group_by(Producto.id, Producto.nombre)
            .order_by(unidades.desc())
            .limit(limite)
        ).all()

        return [
            ProductoVendido(producto_id=id_, nombre=nombre, unidades_vendidas=cantidad, importe=round(importe, 2))
            for id_, nombre, cantidad, importe in filas
        ]

    def stock_bajo(self) -> list[Insumo]:
        return self.insumos.listar_stock_bajo()

    def _condiciones(self, fecha_inicio: date | None, fecha_fin: date | None) -> list:
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise ReglaNegocioError("La fecha_inicio no puede ser posterior a la fecha_fin.")
        return rango_de_fechas(fecha_inicio, fecha_fin)
