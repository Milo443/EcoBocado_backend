import asyncio
from sqlalchemy.orm import Session
from .models import UsuarioORM
from app.db.bd_conections import DatabaseManager
from app.core.config import settings

def _fix_image_url(url: str | None) -> str | None:
    if not url:
        return url
    old_domain = "https://cdn.vooltlab.com"
    if old_domain in url:
        return url.replace(old_domain, settings.MINIO_ENDPOINT)
    return url

# queries para usuarios

# query para obtener usuario por email sincrona es decir que se ejecuta en el hilo principal
def _sync_get_usuario_by_email(email: str) -> dict | None:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        usuario = session.query(UsuarioORM).filter(UsuarioORM.email == email).first()
        if not usuario:
            return None
        # Convertimos a dict simple para evitar problemas de sesión fuera de hilo
        return {
            "id": str(usuario.id),
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": usuario.rol,
            "avatar_url": _fix_image_url(usuario.avatar_url),
            "direccion": usuario.direccion,
            "telefono": usuario.telefono
        }

# query para obtener usuario por email asincrona es decir que se ejecuta en un hilo separado
async def get_usuario_by_email(email: str) -> dict | None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_get_usuario_by_email, email)


# query para crear usuario sincrona es decir que se ejecuta en el hilo principal
def _sync_create_usuario(user_data: dict) -> dict:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        nuevo_usuario = UsuarioORM(**user_data)
        session.add(nuevo_usuario)
        session.commit()
        session.refresh(nuevo_usuario)
        return {
            "id": str(nuevo_usuario.id),
            "nombre": nuevo_usuario.nombre,
            "email": nuevo_usuario.email,
            "rol": nuevo_usuario.rol,
            "direccion": nuevo_usuario.direccion,
            "telefono": nuevo_usuario.telefono
        }

# query para crear usuario asincrona es decir que se ejecuta en un hilo separado
async def create_usuario(user_data: dict) -> dict:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_create_usuario, user_data)

# OTP Queries
from .models import OTPRecord
from datetime import datetime, timedelta
from app.core.config import settings


def _sync_save_otp(email: str, otp_code: str) -> bool:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        # Opcional: Marcar OTPs anteriores como usados/invalidados
        session.query(OTPRecord).filter(OTPRecord.email == email, OTPRecord.is_used == False).update({"is_used": True})
        
        otp_record = OTPRecord(email=email, otp_code=otp_code)
        session.add(otp_record)
        session.commit()
    return True

async def save_otp(email: str, otp_code: str) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_save_otp, email, otp_code)

def _sync_get_valid_otp(email: str, otp_code: str) -> bool:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    expiry_limit = datetime.utcnow() - timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    with Session(engine) as session:
        otp = session.query(OTPRecord).filter(
            OTPRecord.email == email,
            OTPRecord.otp_code == otp_code,
            OTPRecord.is_used == False,
            OTPRecord.created_at >= expiry_limit
        ).first()
        return otp is not None

async def get_valid_otp(email: str, otp_code: str) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_get_valid_otp, email, otp_code)

def _sync_mark_otp_used(email: str, otp_code: str) -> bool:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        session.query(OTPRecord).filter(
            OTPRecord.email == email,
            OTPRecord.otp_code == otp_code
        ).update({"is_used": True})
        session.commit()
    return True

async def mark_otp_used(email: str, otp_code: str) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_mark_otp_used, email, otp_code)


#@author: Camilo Calderon
#por que siempre hay una funcion asincrona y una sincrona?
#por que de esta manera se puede ejecutar el codigo de forma asincrona sin bloquear el hilo principal

def _sync_update_usuario(email: str, update_data: dict) -> dict | None:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        usuario = session.query(UsuarioORM).filter(UsuarioORM.email == email).first()
        if not usuario:
            return None
        
        for key, value in update_data.items():
            if value is not None and hasattr(usuario, key):
                setattr(usuario, key, value)
        
        session.commit()
        session.refresh(usuario)
        return {
            "id": str(usuario.id),
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": usuario.rol,
            "direccion": usuario.direccion,
            "telefono": usuario.telefono,
            "avatar_url": _fix_image_url(usuario.avatar_url),
        }

async def update_usuario(email: str, update_data: dict) -> dict | None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_update_usuario, email, update_data)

from .models import SessionAuditORM
import uuid

def _sync_save_session_audit(usuario_id: str, email: str, ip: str, agent: str):
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        audit = SessionAuditORM(
            usuario_id=uuid.UUID(usuario_id),
            email=email,
            ip_address=ip,
            user_agent=agent
        )
        session.add(audit)
        session.commit()

async def save_session_audit(usuario_id: str, email: str, ip: str, agent: str):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_save_session_audit, usuario_id, email, ip, agent)

def _sync_get_audits() -> list[dict]:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        audits = session.query(SessionAuditORM).order_by(SessionAuditORM.fecha_inicio.desc()).limit(100).all()
        return [
            {
                "id": a.id,
                "usuario_id": a.usuario_id,
                "email": a.email,
                "ip_address": a.ip_address,
                "user_agent": a.user_agent,
                "fecha_inicio": a.fecha_inicio
            } for a in audits
        ]

async def get_audits() -> list[dict]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_get_audits)

