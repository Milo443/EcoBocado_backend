import asyncio
from sqlalchemy.orm import Session
from .models import ReservaORM, EstadoReserva
from ..lotes.models import LoteORM, EstadoLote
from app.db.bd_conections import DatabaseManager
from datetime import datetime, timedelta

def _sync_create_reserva(lote_id: str, receptor_id: str, qr_token: str) -> dict:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    
    with Session(engine) as session:
        # Verificar estado del lote bajo lock (u operar atómicamente)
        lote = session.query(LoteORM).filter(LoteORM.id == lote_id).first()
        if not lote or lote.estado != EstadoLote.ACTIVO:
            return None # Lote no disponible
            
        # Actualizar lote
        lote.estado = EstadoLote.RESERVADO
        
        # Crear reserva
        nueva_reserva = ReservaORM(
            lote_id=lote_id,
            receptor_id=receptor_id,
            estado=EstadoReserva.PENDIENTE,
            codigo_qr_token=qr_token,
            fecha_limite_recogida=datetime.utcnow() + timedelta(hours=2) # 2 horas para recoger
        )
        
        session.add(nueva_reserva)
        session.commit()
        session.refresh(nueva_reserva)
        
        return {
            "id": nueva_reserva.id,
            "lote_id": nueva_reserva.lote_id,
            "receptor_id": nueva_reserva.receptor_id,
            "estado": nueva_reserva.estado,
            "codigo_qr_token": nueva_reserva.codigo_qr_token,
            "fecha_reserva": nueva_reserva.fecha_reserva,
            "fecha_limite_recogida": nueva_reserva.fecha_limite_recogida
        }

async def create_reserva(lote_id: str, receptor_id: str, qr_token: str) -> dict:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_create_reserva, lote_id, receptor_id, qr_token)

def _sync_get_reservas_usuario(receptor_id: str) -> list[dict]:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        reservas = session.query(ReservaORM).filter(ReservaORM.receptor_id == receptor_id).all()
        return [
            {
                "id": r.id,
                "lote_id": r.lote_id,
                "receptor_id": r.receptor_id,
                "estado": r.estado,
                "codigo_qr_token": r.codigo_qr_token,
                "fecha_reserva": r.fecha_reserva,
                "fecha_limite_recogida": r.fecha_limite_recogida,
                "fecha_completada": r.fecha_completada,
                "lote": {
                    "id": r.lote.id,
                    "titulo": r.lote.titulo,
                    "descripcion": r.lote.descripcion,
                    "cantidad": r.lote.cantidad,
                    "categoria": r.lote.categoria,
                    "estado": r.lote.estado,
                    "imagen_url": r.lote.imagen_url,
                    "fecha_publicacion": r.lote.fecha_publicacion,
                    "fecha_caducidad": r.lote.fecha_caducidad,
                    "donante_id": r.lote.donante_id
                }
            } for r in reservas
        ]

async def get_reservas_usuario(receptor_id: str) -> list[dict]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_get_reservas_usuario, receptor_id)

def _sync_completar_reserva(reserva_id: str) -> dict | None:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        reserva = session.query(ReservaORM).filter(ReservaORM.id == reserva_id).first()
        if not reserva or reserva.estado != EstadoReserva.PENDIENTE:
            return None
            
        reserva.estado = EstadoReserva.COMPLETADO
        reserva.fecha_completada = datetime.utcnow()
        reserva.lote.estado = EstadoLote.COMPLETADO
        
        session.commit()
        session.refresh(reserva)
        return {
            "id": reserva.id,
            "estado": reserva.estado,
            "lote_id": reserva.lote_id
        }

async def completar_reserva(reserva_id: str) -> dict | None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_completar_reserva, reserva_id)

def _sync_cancelar_reserva(reserva_id: str) -> bool:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        reserva = session.query(ReservaORM).filter(ReservaORM.id == reserva_id).first()
        if not reserva or reserva.estado != EstadoReserva.PENDIENTE:
            return False
            
        reserva.estado = EstadoReserva.VENCIDO # O CANCELADO if we had it
        reserva.lote.estado = EstadoLote.ACTIVO
        
        session.commit()
        return True

async def cancelar_reserva(reserva_id: str) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_cancelar_reserva, reserva_id)
