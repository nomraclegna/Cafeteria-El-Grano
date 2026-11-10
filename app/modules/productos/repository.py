from sqlalchemy import func, select

from app.core.repository import RepositorioBase
from app.modules.productos.models import Categoria, Producto


class ProductoRepositorio(RepositorioBase[Producto]):
    modelo = Producto

    def obtener_por_nombre(self, nombre: str) -> Producto | None:
        return self.db.scalar(select(Producto).where(func.lower(Producto.nombre) == nombre.lower()))

    def listar_filtrado(self, categoria: Categoria | None, solo_activos: bool) -> list[Producto]:
        consulta = select(Producto).order_by(Producto.categoria, Producto.nombre)
        if categoria is not None:
            consulta = consulta.where(Producto.categoria == categoria)
        if solo_activos:
            consulta = consulta.where(Producto.activo.is_(True))
        return list(self.db.scalars(consulta))
