from fastapi import APIRouter, Query, Depends
from .service import obtener_perfil_usuario, login_request, login_verify, registrar_usuario
from . import schemas
from .schemas import LoginRequest, LoginVerify
from app.core.security import get_current_user

router = APIRouter()

@router.post(
    "/login-otp/request", 
    summary="Solicitar código OTP",
    description="Genera un código de verificación de 6 dígitos y lo envía al correo del usuario vía EmailJS.",
    response_model=schemas.StatusResponse,
    responses={404: {"description": "Usuario no registrado"}, 500: {"description": "Error enviando el correo"}}
)
async def request_otp(data: LoginRequest):
    return await login_request(data.email)

@router.post(
    "/login-otp/verify", 
    summary="Verificar OTP y obtener token",
    description="Valida el código OTP enviado al correo. Si es correcto, emite un JWT Bearer Token válido por 24 horas.",
    response_model=schemas.AuthResponse,
    responses={400: {"description": "Código inválido o expirado"}}
)
async def verify_otp(data: LoginVerify):
    return await login_verify(data.email, data.otp_code)

@router.post(
    "/register", 
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario (DONOR o RECEPTOR) y devuelve un token de acceso inmediato.",
    response_model=schemas.AuthResponse,
    status_code=201,
    responses={400: {"description": "El correo ya está registrado"}}
)
async def register(data: schemas.UsuarioCreate):
    return await registrar_usuario(data)

@router.get(
    "/perfil", 
    summary="Obtener perfil de usuario",
    description="Recupera la información del perfil del usuario autenticado a partir del token Bearer.",
    response_model=schemas.UsuarioPublic,
    responses={401: {"description": "Token inválido o expirado"}, 404: {"description": "Usuario no encontrado"}}
)
async def get_perfil(current_user: dict = Depends(get_current_user)):
    return await obtener_perfil_usuario(current_user["sub"])

@router.put(
    "/perfil", 
    summary="Actualizar perfil",
    description="Permite al usuario autenticado actualizar sus datos personales (nombre, dirección, teléfono).",
    response_model=schemas.UsuarioPublic
)
async def update_perfil(data: schemas.UsuarioUpdate, current_user: dict = Depends(get_current_user)):
    from .queries import update_usuario
    resultado = await update_usuario(current_user["sub"], data.model_dump(exclude_unset=True))
    if not resultado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return resultado
