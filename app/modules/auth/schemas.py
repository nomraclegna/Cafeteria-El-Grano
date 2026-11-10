from pydantic import BaseModel

from app.modules.usuarios.schemas import UsuarioOut


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut
