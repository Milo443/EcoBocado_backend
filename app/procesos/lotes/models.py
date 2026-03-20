from sqlalchemy import String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from datetime import datetime
import uuid
import enum

from app.db.bd_conections import Base

class EstadoLote(str, enum.Enum):
    ACTIVO = "ACTIVO"
    RESERVADO = "RESERVADO"
    COMPLETADO = "COMPLETADO"
    CANCELADO = "CANCELADO"

class CategoriaAlimento(str, enum.Enum):
    PANADERIA = "PANADERIA"
    FRUTAS = "FRUTAS"
    LACTEOS = "LACTEOS"
    VEGETALES = "VEGETALES"
    OTROS = "OTROS"

class LoteORM(Base):
    __tablename__ = "lotes_alimentos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    donante_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    cantidad: Mapped[str] = mapped_column(String(100), nullable=False)
    peso_kg: Mapped[float] = mapped_column(nullable=False, default=0.0)
    categoria: Mapped[CategoriaAlimento] = mapped_column(SQLEnum(CategoriaAlimento), nullable=False)
    estado: Mapped[EstadoLote] = mapped_column(SQLEnum(EstadoLote), default=EstadoLote.ACTIVO)
    imagen_url: Mapped[str] = mapped_column(String(500), nullable=True)
    
    # Geolocalización
    ubicacion = mapped_column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    
    fecha_publicacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fecha_caducidad: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relaciones
    donante = relationship("UsuarioORM", back_populates="lotes")
    reserva = relationship("ReservaORM", back_populates="lote", uselist=False)
