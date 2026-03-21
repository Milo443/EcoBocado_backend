from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional
from .models import EstadoLote, CategoriaAlimento

class LoteBase(BaseModel):
    titulo: str
    descripcion: str
    cantidad: str
    peso_kg: float
    categoria: CategoriaAlimento
    fecha_caducidad: datetime
    imagen_url: Optional[str] = None

class LoteCreate(LoteBase):
    latitud: float
    longitud: float

class LoteUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    cantidad: Optional[str] = None
    peso_kg: Optional[float] = None
    categoria: Optional[CategoriaAlimento] = None
    fecha_caducidad: Optional[datetime] = None
    imagen_url: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class LotePublic(LoteBase):
    id: UUID
    donante_id: UUID
    estado: EstadoLote
    fecha_publicacion: datetime
    reserva_id: Optional[UUID] = None
    codigo_qr_token: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
