from sqlalchemy import String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import enum

from app.db.bd_conections import Base

class EstadoReserva(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    RECOGIDO = "RECOGIDO"
    COMPLETADO = "COMPLETADO"
    VENCIDO = "VENCIDO"

class ReservaORM(Base):
    __tablename__ = "reservas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    lote_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lotes_alimentos.id"), nullable=False)
    receptor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    
    estado: Mapped[EstadoReserva] = mapped_column(SQLEnum(EstadoReserva), default=EstadoReserva.PENDIENTE)
    codigo_qr_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    fecha_reserva: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fecha_limite_recogida: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fecha_completada: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relaciones
    lote = relationship("LoteORM", back_populates="reservas")
    receptor = relationship("UsuarioORM", back_populates="reservas")
