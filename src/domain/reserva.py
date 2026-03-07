from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class EstadoReserva(str, Enum):
    PENDIENTE = "Pendiente"     # Cuando el receptor la aparta
    COMPLETADA = "Completada"   # Cuando el donante escanea el QR
    CANCELADA = "Cancelada"     # Si el receptor no va por ella o se expira

class ReservaBase(BaseModel):
    lote_id: UUID
    receptor_id: UUID

class ReservaCreate(BaseModel):
    """
    Datos que envía el receptor para reservar.
    Nota: Solo necesita enviar el lote_id. 
    El receptor_id lo sacaremos del token JWT por seguridad.
    """
    lote_id: UUID

class ReservaInDB(ReservaBase):
    """Entidad pura de dominio para la reserva transaccional"""
    id: UUID = Field(default_factory=uuid4)
    estado: EstadoReserva = Field(default=EstadoReserva.PENDIENTE)
    codigo_qr_token: str # Aquí guardaremos el hash o token único para el QR
    fecha_reserva: datetime = Field(default_factory=datetime.now)
    fecha_completada: Optional[datetime] = None

class ReservaResponse(ReservaInDB):
    """Modelo para devolver al frontend"""
    pass