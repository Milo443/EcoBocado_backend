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

class LotePublic(LoteBase):
    id: UUID
    donante_id: UUID
    estado: EstadoLote
    fecha_publicacion: datetime
    
    model_config = ConfigDict(from_attributes=True)
