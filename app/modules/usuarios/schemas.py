from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.usuarios.models import Rol


class UsuarioCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str = Field(min_length=3, max_length=80, examples=["María López"])
    usuario: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[A-Za-z0-9_.]+$",
        examples=["maria.lopez"],
        description="Solo letras, números, punto y guion bajo"
    )
    password: str = Field(min_length=8, max_length=72, examples=["Cafe2026*"])
    rol: Rol = Field(default=Rol.CAJERO, examples=["cajero"])


class UsuarioUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: str | None = Field(default=None, min_length=3, max_length=80)
    password: str | None = Field(default=None, min_length=8, max_length=72)
    rol: Rol | None = None
    activo: bool | None = None


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    usuario: str
    rol: Rol
    activo: bool
    creado_en: datetime


class UsuarioResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
