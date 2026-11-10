from datetime import date, datetime, time, timedelta

from sqlalchemy import select

from app.core.repository import RepositorioBase
from app.modules.pedidos.models import EstadoPedido, Pedido


def rango_de_fechas(fecha_inicio: date | None, fecha_fin: date | None) -> list:
    # Convierte las fechas a condiciones de SQLAlchemy incluyendo todo el día de fecha_fin
    condiciones = []
    if fecha_inicio:
        condiciones.append(Pedido.fecha >= datetime.combine(fecha_inicio, time.min))
    if fecha_fin:
        condiciones.append(Pedido.fecha < datetime.combine(fecha_fin + timedelta(days=1), time.min))
    return condiciones


class PedidoRepositorio(RepositorioBase[Pedido]):
    modelo = Pedido

    def listar_filtrado(
        self, estado: EstadoPedido | None, fecha_inicio: date | None, fecha_fin: date | None
    ) -> list[Pedido]:
        consulta = select(Pedido).where(*rango_de_fechas(fecha_inicio, fecha_fin)).order_by(Pedido.id.desc())
        if estado is not None:
            consulta = consulta.where(Pedido.estado == estado)
        return list(self.db.scalars(consulta))
