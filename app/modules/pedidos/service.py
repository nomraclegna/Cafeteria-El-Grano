from collections import defaultdict
from datetime import date

from app.core.database import SesionDB
from app.core.exceptions import ConflictoError, NoEncontradoError, ReglaNegocioError
from app.modules.inventario.models import Insumo, TipoMovimiento
from app.modules.inventario.service import InventarioServicio
from app.modules.pedidos.models import DetallePedido, EstadoPedido, MetodoPago, Pedido
from app.modules.pedidos.repository import PedidoRepositorio
from app.modules.pedidos.schemas import PedidoCreate
from app.modules.productos.repository import ProductoRepositorio
from app.modules.usuarios.models import Usuario

TRANSICIONES = {
    EstadoPedido.PENDIENTE: {EstadoPedido.EN_PREPARACION},
    EstadoPedido.EN_PREPARACION: {EstadoPedido.ENTREGADO},
}


class PedidoServicio:
    def __init__(self, db: SesionDB):
        self.db = db
        self.repo = PedidoRepositorio(db)
        self.productos = ProductoRepositorio(db)
        self.inventario = InventarioServicio(db)

    def listar(self, estado: EstadoPedido | None, fecha_inicio: date | None, fecha_fin: date | None) -> list[Pedido]:
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise ReglaNegocioError("La fecha_inicio no puede ser posterior a la fecha_fin.")
        return self.repo.listar_filtrado(estado, fecha_inicio, fecha_fin)

    def obtener(self, pedido_id: int) -> Pedido:
        pedido = self.repo.obtener(pedido_id)
        if not pedido:
            raise NoEncontradoError(f"El pedido con ID {pedido_id} no existe.")
        return pedido

    def crear(self, datos: PedidoCreate, usuario: Usuario) -> Pedido:
        # Las líneas con el mismo producto y la misma nota se juntan en una sola
        lineas = defaultdict(int)
        for item in datos.items:
            lineas[(item.producto_id, item.notas or None)] += item.cantidad

        detalles = []
        insumos: dict[int, Insumo] = {}
        requerido = defaultdict(float)

        # 1. Validar productos, calcular importes y acumular los insumos que se van a consumir
        for (producto_id, notas), cantidad in lineas.items():
            producto = self.productos.obtener(producto_id)
            if not producto:
                raise NoEncontradoError(f"El producto con ID {producto_id} no existe.")
            if not producto.activo:
                raise ReglaNegocioError(f"El producto '{producto.nombre}' no está disponible.")

            detalles.append(DetallePedido(
                producto=producto,
                cantidad=cantidad,
                notas=notas,
                precio_unitario=producto.precio,
                subtotal=round(producto.precio * cantidad, 2)
            ))

            for ingrediente in producto.receta:
                if not ingrediente.insumo.activo:
                    raise ReglaNegocioError(
                        f"El producto '{producto.nombre}' no está disponible porque el insumo "
                        f"'{ingrediente.insumo.nombre}' está desactivado."
                    )
                insumos[ingrediente.insumo_id] = ingrediente.insumo
                requerido[ingrediente.insumo_id] += ingrediente.cantidad * cantidad

        # 2. Verificar que alcance el inventario antes de modificar cualquier dato
        requerido = {i: round(cantidad, 2) for i, cantidad in requerido.items()}
        faltantes = [
            f"{insumos[i].nombre} (se requieren {cantidad} {insumos[i].unidad}, hay {insumos[i].stock})"
            for i, cantidad in requerido.items()
            if insumos[i].stock < cantidad
        ]
        if faltantes:
            raise ConflictoError("Inventario insuficiente: " + "; ".join(faltantes) + ".")

        # 3. Calcular el total y validar el pago
        total = round(sum(detalle.subtotal for detalle in detalles), 2)
        if datos.metodo_pago == MetodoPago.EFECTIVO:
            if datos.monto_recibido is None:
                raise ReglaNegocioError("Para pagos en efectivo debes indicar el monto_recibido.")
            if datos.monto_recibido < total:
                raise ReglaNegocioError(
                    f"El monto recibido (${datos.monto_recibido:.2f}) es menor al total del pedido (${total:.2f})."
                )
            monto_recibido = round(datos.monto_recibido, 2)
        else:
            monto_recibido = total

        # 4. Registrar el pedido y descontar el inventario en la misma transacción
        pedido = Pedido(
            cliente=datos.cliente or None,
            metodo_pago=datos.metodo_pago,
            total=total,
            monto_recibido=monto_recibido,
            cambio=round(monto_recibido - total, 2),
            usuario=usuario,
            detalles=detalles
        )
        self.repo.agregar(pedido)

        for insumo_id, cantidad in requerido.items():
            self.inventario.aplicar_movimiento(
                insumos[insumo_id], TipoMovimiento.VENTA, -cantidad, usuario.id, f"Pedido #{pedido.id}", pedido.id
            )

        self.db.commit()
        return pedido

    def cambiar_estado(self, pedido_id: int, nuevo_estado: EstadoPedido) -> Pedido:
        pedido = self.obtener(pedido_id)

        if nuevo_estado not in TRANSICIONES.get(pedido.estado, set()):
            raise ReglaNegocioError(f"Un pedido '{pedido.estado}' no puede cambiar a '{nuevo_estado}'.")

        pedido.estado = nuevo_estado
        self.db.commit()
        return pedido

    def cancelar(self, pedido_id: int, motivo: str, usuario: Usuario) -> Pedido:
        pedido = self.obtener(pedido_id)

        if pedido.estado != EstadoPedido.PENDIENTE:
            raise ReglaNegocioError(
                f"Solo se pueden cancelar pedidos pendientes; este pedido está '{pedido.estado}'."
            )

        # Se regresa exactamente lo que se descontó en la venta, aunque la receta haya cambiado después
        for salida in self.inventario.movimientos.listar_por_pedido(pedido.id, TipoMovimiento.VENTA):
            self.inventario.aplicar_movimiento(
                salida.insumo, TipoMovimiento.CANCELACION, -salida.cantidad, usuario.id,
                f"Cancelación del pedido #{pedido.id}", pedido.id
            )

        pedido.estado = EstadoPedido.CANCELADO
        pedido.motivo_cancelacion = motivo
        self.db.commit()
        return pedido
