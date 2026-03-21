import asyncio
import uuid
from sqlalchemy.orm import Session
from .models import ReservaORM, EstadoReserva
from ..lotes.models import LoteORM, EstadoLote
from app.db.bd_conections import DatabaseManager
from datetime import datetime, timedelta

def _sync_create_reserva(lote_id: str, receptor_id: str, qr_token: str) -> dict:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    
    with Session(engine) as session:
        # 1. Verificar si ya existe una reserva ACTIVA (PENDIENTE) para este lote
        reserva_activa = session.query(ReservaORM).filter(
            ReservaORM.lote_id == uuid.UUID(lote_id),
            ReservaORM.estado == EstadoReserva.PENDIENTE
        ).first()
        
        if reserva_activa:
            return None # Lote ya tiene una reserva pendiente
            
        # 2. Verificar estado del lote
        lote = session.query(LoteORM).filter(LoteORM.id == uuid.UUID(lote_id)).first()
        if not lote or lote.estado != EstadoLote.ACTIVO:
            return None # Lote no disponible
            
        # Actualizar lote
        lote.estado = EstadoLote.RESERVADO
        
        # Crear reserva
        nueva_reserva = ReservaORM(
            lote_id=uuid.UUID(lote_id),
            receptor_id=uuid.UUID(receptor_id),
            estado=EstadoReserva.PENDIENTE,
            codigo_qr_token=qr_token,
            fecha_limite_recogida=datetime.utcnow() + timedelta(hours=2) # 2 horas para recoger
        )
        
        session.add(nueva_reserva)
        session.commit()
        session.refresh(nueva_reserva)
        
        # Cargar relaciones para el retorno
        lote = nueva_reserva.lote
        donante = lote.donante if lote else None
        
        return {
            "id": str(nueva_reserva.id),
            "lote_id": str(nueva_reserva.lote_id),
            "receptor_id": str(nueva_reserva.receptor_id),
            "estado": str(nueva_reserva.estado.value) if hasattr(nueva_reserva.estado, 'value') else str(nueva_reserva.estado),
            "codigo_qr_token": str(nueva_reserva.codigo_qr_token),
            "fecha_reserva": nueva_reserva.fecha_reserva,
            "fecha_limite_recogida": nueva_reserva.fecha_limite_recogida,
            "fecha_completada": nueva_reserva.fecha_completada,
            "lote_titulo": str(lote.titulo) if lote else None,
            "donante_nombre": str(donante.nombre) if donante else None,
            "donante_direccion": str(donante.direccion) if donante else None,
            "lote_caduca": lote.fecha_caducidad if lote else None,
            "lote": {
                "id": str(lote.id),
                "titulo": str(lote.titulo),
                "descripcion": str(lote.descripcion),
                "cantidad": str(lote.cantidad),
                "peso_kg": lote.peso_kg,
                "categoria": str(lote.categoria.value) if hasattr(lote.categoria, 'value') else str(lote.categoria),
                "estado": str(lote.estado.value) if hasattr(lote.estado, 'value') else str(lote.estado),
                "imagen_url": str(lote.imagen_url) if lote.imagen_url else None,
                "fecha_publicacion": lote.fecha_publicacion,
                "fecha_caducidad": lote.fecha_caducidad,
                "donante_id": str(lote.donante_id)
            } if lote else None
        }

async def create_reserva(lote_id: str, receptor_id: str, qr_token: str) -> dict:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_create_reserva, lote_id, receptor_id, qr_token)

def _sync_get_reservas_usuario(receptor_id: str, estado: EstadoReserva = None) -> list[dict]:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    try:
        rid = uuid.UUID(receptor_id)
    except:
        return []

    with Session(engine) as session:
        try:
            query = session.query(ReservaORM).filter(ReservaORM.receptor_id == rid)
            if estado:
                query = query.filter(ReservaORM.estado == estado)
            
            reservas = query.all()
            result = []
            for r in reservas:
                # Acceso manual a relaciones
                lote = r.lote
                if not lote: continue
                donante = lote.donante
                
                result.append({
                    "id": str(r.id),
                    "lote_id": str(r.lote_id),
                    "receptor_id": str(r.receptor_id),
                    "estado": str(r.estado.value) if hasattr(r.estado, 'value') else str(r.estado),
                    "codigo_qr_token": str(r.codigo_qr_token),
                    "fecha_reserva": r.fecha_reserva,
                    "fecha_limite_recogida": r.fecha_limite_recogida,
                    "fecha_completada": r.fecha_completada,
                    "lote_titulo": str(lote.titulo),
                    "donante_nombre": str(donante.nombre) if donante else "Desconocido",
                    "donante_direccion": str(donante.direccion) if donante else "No disponible",
                    "lote_caduca": lote.fecha_caducidad,
                    "lote": {
                        "id": str(lote.id),
                        "titulo": str(lote.titulo),
                        "descripcion": str(lote.descripcion),
                        "cantidad": str(lote.cantidad),
                        "peso_kg": lote.peso_kg,
                        "categoria": str(lote.categoria.value) if hasattr(lote.categoria, 'value') else str(lote.categoria),
                        "estado": str(lote.estado.value) if hasattr(lote.estado, 'value') else str(lote.estado),
                        "imagen_url": str(lote.imagen_url) if lote.imagen_url else None,
                        "fecha_publicacion": lote.fecha_publicacion,
                        "fecha_caducidad": lote.fecha_caducidad,
                        "donante_id": str(lote.donante_id)
                    }
                })
            return result
        except Exception as e:
            print(f"Error in _sync_get_reservas_usuario: {e}")
            raise e

async def get_reservas_usuario(receptor_id: str, estado: EstadoReserva = None) -> list[dict]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_get_reservas_usuario, receptor_id, estado)

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
