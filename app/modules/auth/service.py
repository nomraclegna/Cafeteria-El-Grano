from app.core.database import SesionDB
from app.core.exceptions import AccesoDenegadoError, CredencialesInvalidasError
from app.core.security import crear_token, verificar_password
from app.modules.auth.schemas import TokenOut
from app.modules.usuarios.repository import UsuarioRepositorio
from app.modules.usuarios.schemas import UsuarioOut


class AuthServicio:
    def __init__(self, db: SesionDB):
        self.repo = UsuarioRepositorio(db)

    def iniciar_sesion(self, nombre_usuario: str, password: str) -> TokenOut:
        usuario = self.repo.obtener_por_usuario(nombre_usuario.strip().lower())

        # Mismo mensaje para usuario inexistente o contraseña incorrecta, así no se revela qué cuentas existen
        if not usuario or not verificar_password(password, usuario.password_hash):
            raise CredencialesInvalidasError("Usuario o contraseña incorrectos.")

        if not usuario.activo:
            raise AccesoDenegadoError("Tu usuario está desactivado. Contacta al administrador.")

        return TokenOut(
            access_token=crear_token(usuario.id, usuario.rol),
            usuario=UsuarioOut.model_validate(usuario)
        )
