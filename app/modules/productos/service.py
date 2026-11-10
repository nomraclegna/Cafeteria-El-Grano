from app.core.database import SesionDB
from app.core.exceptions import ConflictoError, NoEncontradoError, ReglaNegocioError
from app.modules.inventario.repository import InsumoRepositorio
from app.modules.productos.models import Categoria, Producto, RecetaInsumo
from app.modules.productos.repository import ProductoRepositorio
from app.modules.productos.schemas import ProductoCreate, ProductoUpdate, RecetaItem


class ProductoServicio:
    def __init__(self, db: SesionDB):
        self.db = db
        self.repo = ProductoRepositorio(db)
        self.insumos = InsumoRepositorio(db)

    def listar(self, categoria: Categoria | None, solo_activos: bool) -> list[Producto]:
        return self.repo.listar_filtrado(categoria, solo_activos)

    def obtener(self, producto_id: int) -> Producto:
        producto = self.repo.obtener(producto_id)
        if not producto:
            raise NoEncontradoError(f"El producto con ID {producto_id} no existe.")
        return producto

    def crear(self, datos: ProductoCreate) -> Producto:
        self._validar_nombre_disponible(datos.nombre)

        producto = Producto(
            nombre=datos.nombre,
            descripcion=datos.descripcion,
            categoria=datos.categoria,
            precio=round(datos.precio, 2),
            receta=self._construir_receta(datos.receta)
        )
        self.repo.agregar(producto)
        self.db.commit()
        return producto

    def actualizar(self, producto_id: int, datos: ProductoUpdate) -> Producto:
        producto = self.obtener(producto_id)

        if datos.nombre is not None:
            self._validar_nombre_disponible(datos.nombre, producto.id)
            producto.nombre = datos.nombre
        if datos.descripcion is not None:
            producto.descripcion = datos.descripcion
        if datos.categoria is not None:
            producto.categoria = datos.categoria
        if datos.precio is not None:
            producto.precio = round(datos.precio, 2)
        if datos.activo is not None:
            producto.activo = datos.activo
        if datos.receta is not None:
            producto.receta = self._construir_receta(datos.receta)

        self.db.commit()
        return producto

    def desactivar(self, producto_id: int) -> Producto:
        return self.actualizar(producto_id, ProductoUpdate(activo=False))

    def _validar_nombre_disponible(self, nombre: str, producto_id: int | None = None):
        existente = self.repo.obtener_por_nombre(nombre)
        if existente and existente.id != producto_id:
            raise ConflictoError(f"Ya existe un producto llamado '{nombre}'.")

    def _construir_receta(self, items: list[RecetaItem]) -> list[RecetaInsumo]:
        receta = []
        usados = set()
        for item in items:
            if item.insumo_id in usados:
                raise ReglaNegocioError(f"El insumo con ID {item.insumo_id} está repetido en la receta.")
            usados.add(item.insumo_id)

            insumo = self.insumos.obtener(item.insumo_id)
            if not insumo:
                raise NoEncontradoError(f"El insumo con ID {item.insumo_id} no existe.")
            if not insumo.activo:
                raise ReglaNegocioError(f"El insumo '{insumo.nombre}' está desactivado y no puede usarse en recetas.")

            receta.append(RecetaInsumo(insumo=insumo, cantidad=round(item.cantidad, 2)))
        return receta
