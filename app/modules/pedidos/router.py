from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import SoloAdmin, UsuarioActual, obtener_usuario_actual
from app.modules.pedidos.models import EstadoPedido
from app.modules.pedidos.schemas import CambioEstado, CancelacionPedido, PedidoCreate, PedidoOut
from app.modules.pedidos.service import PedidoServicio

router = APIRouter(prefix="/pedidos", tags=["5. Pedidos"], dependencies=[Depends(obtener_usuario_actual)])

Servicio = Annotated[PedidoServicio, Depends()]


@router.post("", response_model=PedidoOut, status_code=status.HTTP_201_CREATED)
def registrar_pedido(datos: PedidoCreate, servicio: Servicio, usuario: UsuarioActual):
    return servicio.crear(datos, usuario)


@router.get("", response_model=list[PedidoOut])
def listar_pedidos(
    servicio: Servicio,
    estado: EstadoPedido | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None
):
    return servicio.listar(estado, fecha_inicio, fecha_fin)


@router.get("/{pedido_id}", response_model=PedidoOut)
def obtener_pedido(pedido_id: int, servicio: Servicio):
    return servicio.obtener(pedido_id)


@router.patch("/{pedido_id}/estado", response_model=PedidoOut)
def cambiar_estado(pedido_id: int, datos: CambioEstado, servicio: Servicio):
    return servicio.cambiar_estado(pedido_id, EstadoPedido(datos.estado))


@router.post("/{pedido_id}/cancelar", response_model=PedidoOut)
def cancelar_pedido(pedido_id: int, datos: CancelacionPedido, servicio: Servicio, admin: SoloAdmin):
    return servicio.cancelar(pedido_id, datos.motivo, admin)
