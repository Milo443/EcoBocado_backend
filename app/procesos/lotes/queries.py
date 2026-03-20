import asyncio
from sqlalchemy.orm import Session
from .models import LoteORM, EstadoLote
from app.db.bd_conections import DatabaseManager

def _sync_get_lotes_activos() -> list[dict]:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        lotes = session.query(LoteORM).filter(LoteORM.estado == EstadoLote.ACTIVO).all()
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
                "imagen_url": l.imagen_url,
                "fecha_publicacion": l.fecha_publicacion,
                "fecha_caducidad": l.fecha_caducidad
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
            "imagen_url": nuevo_lote.imagen_url,
            "fecha_publicacion": nuevo_lote.fecha_publicacion,
            "fecha_caducidad": nuevo_lote.fecha_caducidad
        }

async def create_lote(lote_data: dict, donante_id: str) -> dict:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_create_lote, lote_data, donante_id)

def _sync_get_lotes_by_donante(donante_id: str) -> list[dict]:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        lotes = session.query(LoteORM).filter(LoteORM.donante_id == donante_id).all()
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
                "imagen_url": l.imagen_url,
                "fecha_publicacion": l.fecha_publicacion,
                "fecha_caducidad": l.fecha_caducidad
            } for l in lotes
        ]

async def get_lotes_by_donante(donante_id: str) -> list[dict]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_get_lotes_by_donante, donante_id)
