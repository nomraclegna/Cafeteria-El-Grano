from app.core.database import SesionDB
from app.core.exceptions import ConflictoError, NoEncontradoError, ReglaNegocioError
from app.modules.inventario.models import Insumo, MovimientoInventario, TipoMovimiento
from app.modules.inventario.repository import InsumoRepositorio, MovimientoRepositorio
from app.modules.inventario.schemas import EntradaCreate, InsumoCreate, InsumoUpdate, MermaCreate


class InventarioServicio:
    def __init__(self, db: SesionDB):
        self.db = db
        self.insumos = InsumoRepositorio(db)
        self.movimientos = MovimientoRepositorio(db)

    def listar(self, solo_activos: bool) -> list[Insumo]:
        return self.insumos.listar_filtrado(solo_activos)

    def obtener(self, insumo_id: int) -> Insumo:
        insumo = self.insumos.obtener(insumo_id)
        if not insumo:
            raise NoEncontradoError(f"El insumo con ID {insumo_id} no existe.")
        return insumo

    def crear(self, datos: InsumoCreate, usuario_id: int) -> Insumo:
        if self.insumos.obtener_por_nombre(datos.nombre):
            raise ConflictoError(f"Ya existe un insumo llamado '{datos.nombre}'.")

        insumo = Insumo(nombre=datos.nombre, unidad=datos.unidad, stock=0, stock_minimo=round(datos.stock_minimo, 2))
        self.insumos.agregar(insumo)

        if datos.stock_inicial > 0:
            self.aplicar_movimiento(insumo, TipoMovimiento.ENTRADA, datos.stock_inicial, usuario_id, "Inventario inicial")

        self.db.commit()
        return insumo

    def actualizar(self, insumo_id: int, datos: InsumoUpdate) -> Insumo:
        insumo = self.obtener(insumo_id)

        if datos.nombre is not None:
            existente = self.insumos.obtener_por_nombre(datos.nombre)
            if existente and existente.id != insumo.id:
                raise ConflictoError(f"Ya existe un insumo llamado '{datos.nombre}'.")
            insumo.nombre = datos.nombre
        if datos.stock_minimo is not None:
            insumo.stock_minimo = round(datos.stock_minimo, 2)
        if datos.activo is not None:
            insumo.activo = datos.activo

        self.db.commit()
        return insumo

    def desactivar(self, insumo_id: int) -> Insumo:
        return self.actualizar(insumo_id, InsumoUpdate(activo=False))

    def registrar_entrada(self, insumo_id: int, datos: EntradaCreate, usuario_id: int) -> MovimientoInventario:
        insumo = self.obtener(insumo_id)
        if not insumo.activo:
            raise ReglaNegocioError(f"El insumo '{insumo.nombre}' está desactivado.")

        movimiento = self.aplicar_movimiento(
            insumo, TipoMovimiento.ENTRADA, datos.cantidad, usuario_id, datos.motivo or "Compra a proveedor"
        )
        self.db.commit()
        return movimiento

    def registrar_merma(self, insumo_id: int, datos: MermaCreate, usuario_id: int) -> MovimientoInventario:
        insumo = self.obtener(insumo_id)
        if datos.cantidad > insumo.stock:
            raise ReglaNegocioError(
                f"No se puede registrar una merma de {datos.cantidad} {insumo.unidad}: "
                f"solo hay {insumo.stock} {insumo.unidad} de '{insumo.nombre}'."
            )

        movimiento = self.aplicar_movimiento(insumo, TipoMovimiento.MERMA, -datos.cantidad, usuario_id, datos.motivo)
        self.db.commit()
        return movimiento

    def listar_movimientos(
        self, insumo_id: int | None, tipo: TipoMovimiento | None, limite: int
    ) -> list[MovimientoInventario]:
        return self.movimientos.listar_filtrado(insumo_id, tipo, limite)

    def aplicar_movimiento(
        self,
        insumo: Insumo,
        tipo: TipoMovimiento,
        cantidad: float,
        usuario_id: int,
        motivo: str | None = None,
        pedido_id: int | None = None
    ) -> MovimientoInventario:
        # Único punto donde cambia el stock, así cada cambio queda registrado en el historial.
        # No hace commit: quien lo llama decide cuándo confirmar la transacción.
        insumo.stock = round(insumo.stock + cantidad, 2)
        movimiento = MovimientoInventario(
            insumo=insumo,
            tipo=tipo,
            cantidad=round(cantidad, 2),
            stock_resultante=insumo.stock,
            motivo=motivo,
            pedido_id=pedido_id,
            usuario_id=usuario_id
        )
        return self.movimientos.agregar(movimiento)
