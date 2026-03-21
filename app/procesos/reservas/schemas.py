from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from .models import EstadoReserva
from ..lotes.schemas import LotePublic

class ReservaCreate(BaseModel):
    lote_id: UUID

class ReservaPublic(BaseModel):
    id: UUID
    lote_id: UUID
    receptor_id: UUID
    estado: EstadoReserva
    codigo_qr_token: str
    fecha_reserva: datetime
    fecha_limite_recogida: datetime
    fecha_completada: datetime | None = None
    
    # Campos aplanados para el frontend
    lote_titulo: str | None = None
    donante_nombre: str | None = None
    donante_direccion: str | None = None
    lote_caduca: datetime | None = None
    
    # Opcional: Incluir el lote para mayor detalle en el frontend
    lote: LotePublic | None = None

    model_config = ConfigDict(from_attributes=True)
