from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.database import Base, engine
from app.core.exceptions import ErrorNegocio
from app.modules.auth.router import router as auth_router
from app.modules.inventario.router import router as inventario_router
from app.modules.pedidos.router import router as pedidos_router
from app.modules.productos.router import router as productos_router
from app.modules.reportes.router import router as reportes_router
from app.modules.usuarios.router import router as usuarios_router
from app.seed import cargar_datos_iniciales

CARPETA_FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    cargar_datos_iniciales()
    yield


app = FastAPI(
    title="API REST - Cafetería El Grano",
    description="Administración de productos, inventario de insumos, pedidos, ventas e historial de movimientos",
    version="1.0.0",
    lifespan=lifespan
)


@app.exception_handler(ErrorNegocio)
def manejar_error_negocio(request: Request, exc: ErrorNegocio):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensaje})


for router in (auth_router, usuarios_router, productos_router, inventario_router, pedidos_router, reportes_router):
    app.include_router(router, prefix="/v1/api")

app.mount("/app", StaticFiles(directory=CARPETA_FRONTEND, html=True), name="frontend")


@app.get("/", include_in_schema=False)
def inicio():
    return RedirectResponse(url="/app/")
