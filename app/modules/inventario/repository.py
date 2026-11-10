from sqlalchemy import func, select

from app.core.repository import RepositorioBase
from app.modules.inventario.models import Insumo, MovimientoInventario, TipoMovimiento


class InsumoRepositorio(RepositorioBase[Insumo]):
    modelo = Insumo

    def obtener_por_nombre(self, nombre: str) -> Insumo | None:
        return self.db.scalar(select(Insumo).where(func.lower(Insumo.nombre) == nombre.lower()))

    def listar_filtrado(self, solo_activos: bool) -> list[Insumo]:
        consulta = select(Insumo).order_by(Insumo.nombre)
        if solo_activos:
            consulta = consulta.where(Insumo.activo.is_(True))
        return list(self.db.scalars(consulta))

    def listar_stock_bajo(self) -> list[Insumo]:
        consulta = (
            select(Insumo)
            .where(Insumo.activo.is_(True), Insumo.stock <= Insumo.stock_minimo)
            .order_by(Insumo.nombre)
        )
        return list(self.db.scalars(consulta))


class MovimientoRepositorio(RepositorioBase[MovimientoInventario]):
    modelo = MovimientoInventario

    def listar_filtrado(
        self, insumo_id: int | None, tipo: TipoMovimiento | None, limite: int
    ) -> list[MovimientoInventario]:
        consulta = select(MovimientoInventario).order_by(MovimientoInventario.id.desc()).limit(limite)
        if insumo_id is not None:
            consulta = consulta.where(MovimientoInventario.insumo_id == insumo_id)
        if tipo is not None:
            consulta = consulta.where(MovimientoInventario.tipo == tipo)
        return list(self.db.scalars(consulta))

    def listar_por_pedido(self, pedido_id: int, tipo: TipoMovimiento) -> list[MovimientoInventario]:
        consulta = select(MovimientoInventario).where(
            MovimientoInventario.pedido_id == pedido_id,
            MovimientoInventario.tipo == tipo
        )
        return list(self.db.scalars(consulta))
