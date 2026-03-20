from pydantic import BaseModel, EmailStr
from typing import Optional
from app.procesos.usuarios.models import RolUsuario

class LoginRequest(BaseModel):
    email: EmailStr

class LoginVerify(BaseModel):
    email: EmailStr
    otp_code: str

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: RolUsuario
    direccion: str
    telefono: str
    avatar_url: Optional[str] = None

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None

class UsuarioPublic(BaseModel):
    id: str
    nombre: str
    email: EmailStr
    rol: RolUsuario
    direccion: str
    telefono: str
    avatar_url: Optional[str] = None

class AuthResponse(BaseModel):
    exito: bool
    access_token: str
    token_type: str
    usuario: UsuarioPublic

class StatusResponse(BaseModel):
    exito: bool
    mensaje: str
