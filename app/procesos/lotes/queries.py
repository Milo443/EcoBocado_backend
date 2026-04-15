import asyncio
from sqlalchemy.orm import Session
from .models import LoteORM, EstadoLote
from app.db.bd_conections import DatabaseManager

from app.core.config import settings

def _fix_image_url(url: str | None) -> str | None:
    if not url:
        return url
    # Si la URL contiene el dominio viejo que está fallando/secuestrado, lo reemplazamos por el actual
    old_domain = "https://cdn.vooltlab.com"
    if old_domain in url:
        return url.replace(old_domain, settings.MINIO_ENDPOINT)
    return url

def _sync_get_lotes_activos() -> list[dict]:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        lotes = session.query(LoteORM).filter(LoteORM.estado == EstadoLote.ACTIVO, LoteORM.esta_borrado == False).all()
        return [
            {
                "id": l.id,
                "donante_id": l.donante_id,
                "titulo": l.titulo,
                "descripcion": l.descripcion,
                "cantidad": l.cantidad,
                "peso_kg": l.peso_kg,
                "categoria": l.categoria,
                "estado": l.estado,
                "imagen_url": _fix_image_url(l.imagen_url),
                "fecha_publicacion": l.fecha_publicacion,
                "fecha_caducidad": l.fecha_caducidad,
                "reserva_id": None,
                "codigo_qr_token": None
            } for l in lotes
        ]

async def get_lotes_activos() -> list[dict]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_get_lotes_activos)

def _sync_create_lote(lote_data: dict, donante_id: str) -> dict:
    from geoalchemy2.functions import ST_GeomFromText
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    
    lat = lote_data.pop("latitud")
    lng = lote_data.pop("longitud")
    
    with Session(engine) as session:
        nuevo_lote = LoteORM(
            **lote_data,
            donante_id=donante_id,
            ubicacion=f"POINT({lng} {lat})"
        )
        session.add(nuevo_lote)
        session.commit()
        session.refresh(nuevo_lote)
        return {
            "id": nuevo_lote.id,
            "donante_id": nuevo_lote.donante_id,
            "titulo": nuevo_lote.titulo,
            "descripcion": nuevo_lote.descripcion,
            "cantidad": nuevo_lote.cantidad,
            "peso_kg": nuevo_lote.peso_kg,
            "categoria": nuevo_lote.categoria,
            "estado": nuevo_lote.estado,
            "imagen_url": _fix_image_url(nuevo_lote.imagen_url),
            "fecha_publicacion": nuevo_lote.fecha_publicacion,
            "fecha_caducidad": nuevo_lote.fecha_caducidad,
            "reserva_id": None,
            "codigo_qr_token": None
        }

async def create_lote(lote_data: dict, donante_id: str) -> dict:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_create_lote, lote_data, donante_id)

from ..reservas.models import ReservaORM, EstadoReserva

def _sync_get_lotes_by_donante(donante_id: str) -> list[dict]:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        # Join con Reservas para obtener el ID de la reserva activa si existe
        query = session.query(LoteORM, ReservaORM.id, ReservaORM.codigo_qr_token).outerjoin(
            ReservaORM, 
            (LoteORM.id == ReservaORM.lote_id) & 
            (ReservaORM.estado.in_([EstadoReserva.PENDIENTE, EstadoReserva.RECOGIDO]))
        ).filter(LoteORM.donante_id == donante_id, LoteORM.esta_borrado == False)
        
        results = query.all()
        
        return [
            {
                "id": l.id,
                "donante_id": l.donante_id,
                "titulo": l.titulo,
                "descripcion": l.descripcion,
                "cantidad": l.cantidad,
                "peso_kg": l.peso_kg,
                "categoria": l.categoria,
                "estado": l.estado,
                "imagen_url": _fix_image_url(l.imagen_url),
                "fecha_publicacion": l.fecha_publicacion,
                "fecha_caducidad": l.fecha_caducidad,
                "reserva_id": str(reserva_id) if reserva_id else None,
                "codigo_qr_token": str(codigo_qr_token) if codigo_qr_token else None
            } for l, reserva_id, codigo_qr_token in results
        ]

async def get_lotes_by_donante(donante_id: str) -> list[dict]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_get_lotes_by_donante, donante_id)

def _sync_delete_lote(lote_id: str) -> bool:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        lote = session.query(LoteORM).filter(LoteORM.id == lote_id).first()
        if not lote:
            return False
        lote.esta_borrado = True
        session.commit()
        return True

async def delete_lote(lote_id: str) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_delete_lote, lote_id)

def _sync_update_lote(lote_id: str, lote_data: dict) -> dict | None:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    
    # Procesar ubicación si viene en los campos
    lat = lote_data.pop("latitud", None)
    lng = lote_data.pop("longitud", None)
    
    with Session(engine) as session:
        lote = session.query(LoteORM).filter(LoteORM.id == lote_id, LoteORM.esta_borrado == False).first()
        if not lote:
            return None
            
        # Actualizar campos básicos
        for key, value in lote_data.items():
            if value is not None:
                setattr(lote, key, value)
        
        # Actualizar ubicación si aplica
        if lat is not None and lng is not None:
            lote.ubicacion = f"POINT({lng} {lat})"
            
        session.commit()
        session.refresh(lote)
        return {
            "id": lote.id,
            "donante_id": lote.donante_id,
            "titulo": lote.titulo,
            "descripcion": lote.descripcion,
            "cantidad": lote.cantidad,
            "peso_kg": lote.peso_kg,
            "categoria": lote.categoria,
            "estado": lote.estado,
            "imagen_url": _fix_image_url(lote.imagen_url),
            "fecha_publicacion": lote.fecha_publicacion,
            "fecha_caducidad": lote.fecha_caducidad,
            "reserva_id": None,
            "codigo_qr_token": None
        }

async def update_lote(lote_id: str, lote_data: dict) -> dict | None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_update_lote, lote_id, lote_data)
