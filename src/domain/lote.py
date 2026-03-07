from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class EstadoLote(str, Enum):
    ACTIVO = "Activo"
    RESERVADO = "Reservado"
    EXPIRADO = "Expirado"

class LoteAlimentoBase(BaseModel):
    titulo: str
    descripcion: str
    fotografia_url: Optional[str] = None # Será llenado tras subir a MinIO
    cantidad: str
    latitud: float
    longitud: float
    fecha_hora_caducidad: datetime

class LoteAlimentoCreate(LoteAlimentoBase):
    """Datos necesarios que envía el Donante desde el frontend para publicar"""
    pass # El donante_id se tomará del token JWT, no del formulario

class LoteAlimentoInDB(LoteAlimentoBase):
    """Entidad pura de dominio para el alimento"""
    id: UUID = Field(default_factory=uuid4)
    donante_id: UUID
    estado: EstadoLote = Field(default=EstadoLote.ACTIVO)
    fecha_publicacion: datetime = Field(default_factory=datetime.now)