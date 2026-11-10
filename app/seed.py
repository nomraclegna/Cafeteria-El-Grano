from sqlalchemy import func, select

from app.core.config import settings
from app.core.database import SesionLocal
from app.modules.inventario.models import Unidad
from app.modules.inventario.schemas import InsumoCreate
from app.modules.inventario.service import InventarioServicio
from app.modules.productos.models import Categoria
from app.modules.productos.schemas import ProductoCreate, RecetaItem
from app.modules.productos.service import ProductoServicio
from app.modules.usuarios.models import Rol, Usuario
from app.modules.usuarios.schemas import UsuarioCreate
from app.modules.usuarios.service import UsuarioServicio

INSUMOS = [
    ("Café en grano", Unidad.GRAMOS, 5000, 1000),
    ("Leche entera", Unidad.MILILITROS, 10000, 2000),
    ("Chocolate en polvo", Unidad.GRAMOS, 2000, 300),
    ("Jarabe de vainilla", Unidad.MILILITROS, 1000, 200),
    ("Hielo", Unidad.GRAMOS, 8000, 1000),
    ("Vaso 12 oz", Unidad.PIEZAS, 200, 50),
    ("Croissant", Unidad.PIEZAS, 30, 10),
    ("Rebanada de pastel de zanahoria", Unidad.PIEZAS, 12, 4),
]

# (nombre, descripción, categoría, precio, [(insumo, cantidad por unidad)])
PRODUCTOS = [
    ("Espresso", "Shot doble de café", Categoria.BEBIDA_CALIENTE, 35,
     [("Café en grano", 18), ("Vaso 12 oz", 1)]),
    ("Americano", "Espresso con agua caliente", Categoria.BEBIDA_CALIENTE, 40,
     [("Café en grano", 18), ("Vaso 12 oz", 1)]),
    ("Capuchino", "Espresso con leche espumada", Categoria.BEBIDA_CALIENTE, 55,
     [("Café en grano", 18), ("Leche entera", 150), ("Vaso 12 oz", 1)]),
    ("Latte de vainilla", "Espresso, leche y jarabe de vainilla", Categoria.BEBIDA_CALIENTE, 65,
     [("Café en grano", 18), ("Leche entera", 200), ("Jarabe de vainilla", 20), ("Vaso 12 oz", 1)]),
    ("Chocolate caliente", "Chocolate con leche", Categoria.BEBIDA_CALIENTE, 50,
     [("Chocolate en polvo", 30), ("Leche entera", 250), ("Vaso 12 oz", 1)]),
    ("Frappé moka", "Café, chocolate, leche y hielo", Categoria.BEBIDA_FRIA, 70,
     [("Café en grano", 18), ("Chocolate en polvo", 20), ("Leche entera", 150), ("Hielo", 200), ("Vaso 12 oz", 1)]),
    ("Vaso con hielo", "Cortesía para clientes", Categoria.BEBIDA_FRIA, 0,
     [("Hielo", 150), ("Vaso 12 oz", 1)]),
    ("Croissant", "Croissant de mantequilla", Categoria.ALIMENTO, 38,
     [("Croissant", 1)]),
    ("Pastel de zanahoria", "Rebanada individual", Categoria.POSTRE, 60,
     [("Rebanada de pastel de zanahoria", 1)]),
]


def cargar_datos_iniciales():
    with SesionLocal() as db:
        if db.scalar(select(func.count(Usuario.id))) > 0:
            return

        usuarios = UsuarioServicio(db)
        admin = usuarios.crear(UsuarioCreate(
            nombre="Administrador", usuario=settings.admin_usuario, password=settings.admin_password, rol=Rol.ADMIN
        ))
        usuarios.crear(UsuarioCreate(
            nombre="Cajero de turno", usuario=settings.cajero_usuario, password=settings.cajero_password, rol=Rol.CAJERO
        ))

        if not settings.cargar_datos_demo:
            return

        inventario = InventarioServicio(db)
        ids_insumos = {}
        for nombre, unidad, stock, minimo in INSUMOS:
            insumo = inventario.crear(
                InsumoCreate(nombre=nombre, unidad=unidad, stock_inicial=stock, stock_minimo=minimo), admin.id
            )
            ids_insumos[nombre] = insumo.id

        productos = ProductoServicio(db)
        for nombre, descripcion, categoria, precio, receta in PRODUCTOS:
            productos.crear(ProductoCreate(
                nombre=nombre,
                descripcion=descripcion,
                categoria=categoria,
                precio=precio,
                receta=[RecetaItem(insumo_id=ids_insumos[insumo], cantidad=cantidad) for insumo, cantidad in receta]
            ))
