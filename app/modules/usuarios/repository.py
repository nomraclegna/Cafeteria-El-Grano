from sqlalchemy import select

from app.core.repository import RepositorioBase
from app.modules.usuarios.models import Usuario


class UsuarioRepositorio(RepositorioBase[Usuario]):
    modelo = Usuario

    def obtener_por_usuario(self, usuario: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.usuario == usuario))
