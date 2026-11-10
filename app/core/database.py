from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

es_sqlite = settings.database_url.startswith("sqlite")

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if es_sqlite else {}
)

if es_sqlite:
    # SQLite no valida llaves foráneas a menos que se active en cada conexión
    @event.listens_for(engine, "connect")
    def activar_llaves_foraneas(conexion, _):
        cursor = conexion.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SesionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def obtener_db():
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()


SesionDB = Annotated[Session, Depends(obtener_db)]
