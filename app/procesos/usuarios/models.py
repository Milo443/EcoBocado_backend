from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import enum

from app.db.bd_conections import Base

class RolUsuario(str, enum.Enum):
    DONOR = "DONOR"
    RECEPTOR = "RECEPTOR"

class UsuarioORM(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(SQLEnum(RolUsuario), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=True)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    telefono: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    lotes = relationship("LoteORM", back_populates="donante")
    reservas = relationship("ReservaORM", back_populates="receptor")

class OTPRecord(Base):
    __tablename__ = "otps"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    otp_code: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_used: Mapped[bool] = mapped_column(default=False)

class SessionAuditORM(Base):
    __tablename__ = "sesiones_auditoria"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relación
    usuario = relationship("UsuarioORM")
