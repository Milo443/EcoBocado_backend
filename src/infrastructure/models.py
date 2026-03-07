import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

# Importamos la Base que creamos en database.py
from src.infrastructure.database import Base

# Importamos los Enums puros de nuestro dominio
from src.domain.usuario import RolUsuario
from src.domain.lote import EstadoLote
from src.domain.reserva import EstadoReserva


class UsuarioORM(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(SQLEnum(RolUsuario), nullable=False)
    nombre_perfil: Mapped[str] = mapped_column(String(255), nullable=False)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    contacto: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relaciones para navegar fácilmente desde un usuario a sus lotes o reservas
    lotes_publicados = relationship("LoteAlimentoORM", back_populates="donante", cascade="all, delete-orphan")
    reservas_realizadas = relationship("ReservaORM", back_populates="receptor", cascade="all, delete-orphan")


class LoteAlimentoORM(Base):
    __tablename__ = "lotes_alimentos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    donante_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fotografia_url: Mapped[str] = mapped_column(String(500), nullable=True)
    cantidad: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Campo espacial PostGIS (SRID 4326 es el estándar GPS WGS 84)
    ubicacion: Mapped[str] = mapped_column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    
    fecha_hora_caducidad: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    fecha_publicacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    estado: Mapped[EstadoLote] = mapped_column(SQLEnum(EstadoLote), default=EstadoLote.ACTIVO, nullable=False)

    # Relaciones
    donante = relationship("UsuarioORM", back_populates="lotes_publicados")
    reserva = relationship("ReservaORM", back_populates="lote", uselist=False) # Relación 1 a 1 (un lote, una reserva activa)


class ReservaORM(Base):
    __tablename__ = "reservas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    lote_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lotes_alimentos.id"), nullable=False, unique=True)
    receptor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    
    estado: Mapped[EstadoReserva] = mapped_column(SQLEnum(EstadoReserva), default=EstadoReserva.PENDIENTE, nullable=False)
    codigo_qr_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    fecha_reserva: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    fecha_completada: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relaciones
    lote = relationship("LoteAlimentoORM", back_populates="reserva")
    receptor = relationship("UsuarioORM", back_populates="reservas_realizadas")