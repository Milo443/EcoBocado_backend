from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4
from datetime import datetime

class RolUsuario(str, Enum):
    DONANTE = "Donante"
    RECEPTOR = "Receptor"

class UsuarioBase(BaseModel):
    """Atributos compartidos para creación y lectura"""
    email: EmailStr
    rol: RolUsuario
    nombre_perfil: str # Nombre del local o de la fundación
    direccion: str
    contacto: str

class UsuarioCreate(UsuarioBase):
    """Modelo usado exclusivamente cuando el usuario se registra (incluye password)"""
    password: str

class UsuarioInDB(UsuarioBase):
    """Modelo puro de dominio (Entidad completa)"""
    id: UUID = Field(default_factory=uuid4)
    password_hash: str
    fecha_registro: datetime = Field(default_factory=datetime.now)

class UsuarioResponse(UsuarioBase):
    """Modelo para devolver al frontend (SIN el password_hash por seguridad)"""
    id: UUID
    fecha_registro: datetime