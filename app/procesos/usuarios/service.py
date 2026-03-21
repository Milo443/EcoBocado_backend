import random
import string
from fastapi import HTTPException
from . import queries
from app.core.email_service import send_otp_email
from app.core.auth import create_access_token
from app.core.security_utils import hash_password
from . import schemas

async def obtener_perfil_usuario(email: str) -> dict:
    usuario = await queries.get_usuario_by_email(email)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

async def login_request(email: str):
    usuario = await queries.get_usuario_by_email(email)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no registrado")
    
    # Generar OTP de 6 dígitos
    otp_code = ''.join(random.choices(string.digits, k=6))
    
    # Guardar en DB
    await queries.save_otp(email, otp_code)
    
    # Enviar Email
    enviado = await send_otp_email(email, otp_code)
    if not enviado:
        raise HTTPException(status_code=500, detail="Error enviando el código de verificación")
    
    return {"exito": True, "mensaje": "Código enviado a su correo"}

async def login_verify(email: str, otp_code: str, ip: str = None, user_agent: str = None):
    es_valido = await queries.get_valid_otp(email, otp_code)
    if not es_valido:
        raise HTTPException(status_code=400, detail="Código inválido o expirado")
    
    # Marcar como usado
    await queries.mark_otp_used(email, otp_code)
    
    # Obtener usuario para el token
    usuario = await queries.get_usuario_by_email(email)
    
    # Generar JWT
    token = create_access_token(data={
        "sub": usuario["email"],
        "id": usuario["id"],
        "role": usuario["rol"]
    })
    
    # Auditoría de Sesión
    await queries.save_session_audit(usuario["id"], usuario["email"], ip, user_agent)
    
    return {
        "exito": True,
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario
    }

async def registrar_usuario(usuario_data: schemas.UsuarioCreate):
    # Verificar si ya existe
    existente = await queries.get_usuario_by_email(usuario_data.email)
    if existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # Preparar datos
    data_dict = usuario_data.model_dump()
    password = data_dict.pop("password")
    data_dict["password_hash"] = hash_password(password)
    
    # Crear usuario
    nuevo_usuario = await queries.create_usuario(data_dict)
    
    # Generar token inicial
    token = create_access_token(data={
        "sub": nuevo_usuario["email"],
        "id": nuevo_usuario["id"],
        "role": nuevo_usuario["rol"]
    })
    
    return {
        "exito": True,
        "mensaje": "Usuario registrado exitosamente",
        "access_token": token,
        "token_type": "bearer",
        "usuario": nuevo_usuario
    }
