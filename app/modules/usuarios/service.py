from app.core.database import SesionDB
from app.core.exceptions import ConflictoError, NoEncontradoError, ReglaNegocioError
from app.core.security import hashear_password
from app.modules.usuarios.models import Rol, Usuario
from app.modules.usuarios.repository import UsuarioRepositorio
from app.modules.usuarios.schemas import UsuarioCreate, UsuarioUpdate


class UsuarioServicio:
    def __init__(self, db: SesionDB):
        self.db = db
        self.repo = UsuarioRepositorio(db)

    def listar(self) -> list[Usuario]:
        return self.repo.listar()

    def obtener(self, usuario_id: int) -> Usuario:
        usuario = self.repo.obtener(usuario_id)
        if not usuario:
            raise NoEncontradoError(f"El usuario con ID {usuario_id} no existe.")
        return usuario

    def crear(self, datos: UsuarioCreate) -> Usuario:
        nombre_usuario = datos.usuario.lower()
        if self.repo.obtener_por_usuario(nombre_usuario):
            raise ConflictoError(f"El usuario '{nombre_usuario}' ya está registrado.")

        usuario = Usuario(
            nombre=datos.nombre,
            usuario=nombre_usuario,
            password_hash=hashear_password(datos.password),
            rol=datos.rol
        )
        self.repo.agregar(usuario)
        self.db.commit()
        return usuario

    def actualizar(self, usuario_id: int, datos: UsuarioUpdate, usuario_actual: Usuario) -> Usuario:
        usuario = self.obtener(usuario_id)

        # Evita que el sistema se quede sin un administrador con acceso
        if usuario.id == usuario_actual.id and (datos.activo is False or datos.rol == Rol.CAJERO):
            raise ReglaNegocioError("No puedes desactivar tu propia cuenta ni quitarte el rol de administrador.")

        if datos.nombre is not None:
            usuario.nombre = datos.nombre
        if datos.password is not None:
            usuario.password_hash = hashear_password(datos.password)
        if datos.rol is not None:
            usuario.rol = datos.rol
        if datos.activo is not None:
            usuario.activo = datos.activo

        self.db.commit()
        return usuario

    def desactivar(self, usuario_id: int, usuario_actual: Usuario) -> Usuario:
        return self.actualizar(usuario_id, UsuarioUpdate(activo=False), usuario_actual)
