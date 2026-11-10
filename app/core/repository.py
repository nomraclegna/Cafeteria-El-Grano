from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import Base

ModeloT = TypeVar("ModeloT", bound=Base)


# Patrón Repository: concentra el acceso a datos para que los servicios no escriban consultas directamente
class RepositorioBase(Generic[ModeloT]):
    modelo: type[ModeloT]

    def __init__(self, db: Session):
        self.db = db

    def obtener(self, id_entidad: int) -> ModeloT | None:
        return self.db.get(self.modelo, id_entidad)

    def listar(self) -> list[ModeloT]:
        return list(self.db.scalars(select(self.modelo).order_by(self.modelo.id)))

    def agregar(self, entidad: ModeloT) -> ModeloT:
        self.db.add(entidad)
        self.db.flush()
        return entidad
