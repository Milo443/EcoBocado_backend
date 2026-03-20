import asyncio
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..lotes.models import LoteORM, EstadoLote
from ..reservas.models import ReservaORM, EstadoReserva
from ..usuarios.models import UsuarioORM, RolUsuario
from app.db.bd_conections import DatabaseManager
from datetime import datetime, timedelta

def _sync_get_global_impact() -> dict:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        # 1. Total Rescatado (kg)
        total_kg = session.query(func.sum(LoteORM.peso_kg)).filter(LoteORM.estado == EstadoLote.COMPLETADO).scalar() or 0.0
        
        # 2. Personas Ayudadas (Receptores únicos con reservas completadas)
        personas = session.query(func.count(func.distinct(ReservaORM.receptor_id))).filter(ReservaORM.estado == EstadoReserva.COMPLETADO).scalar() or 0
        
        # 3. Aliados Red (Donadores únicos)
        aliados = session.query(func.count(UsuarioORM.id)).filter(UsuarioORM.rol == RolUsuario.DONOR).scalar() or 0
        
        # 4. CO2 Mitigado (Factor: 2.5kg CO2 por cada 1kg de comida)
        co2 = round(total_kg * 2.5, 2)
        
        return {
            "total_rescatado_kg": round(total_kg, 2),
            "personas_ayudadas": personas,
            "aliados_red": aliados,
            "co2_mitigado_kg": co2
        }

async def get_global_impact() -> dict:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_get_global_impact)

def _sync_get_donor_dashboard(donante_id: str) -> dict:
    engine = DatabaseManager._get_engine('postgres_ecobocado')
    with Session(engine) as session:
        # Peso rescatado por este donador
        peso_donador = session.query(func.sum(LoteORM.peso_kg)).filter(
            LoteORM.donante_id == donante_id, 
            LoteORM.estado == EstadoLote.COMPLETADO
        ).scalar() or 0.0
        
        # Lotes actualmente activos
        lotes_activos = session.query(func.count(LoteORM.id)).filter(
            LoteORM.donante_id == donante_id, 
            LoteORM.estado == EstadoLote.ACTIVO
        ).scalar() or 0
        
        # Entregas hoy (completadas en las últimas 24h)
        hoy = datetime.utcnow() - timedelta(days=1)
        entregas_hoy = session.query(func.count(ReservaORM.id)).join(LoteORM).filter(
            LoteORM.donante_id == donante_id,
            ReservaORM.estado == EstadoReserva.COMPLETADO,
            ReservaORM.fecha_completada >= hoy
        ).scalar() or 0
        
        return {
            "peso_rescatado_kg": round(peso_donador, 2),
            "lotes_activos": lotes_activos,
            "entregas_hoy": entregas_hoy
        }

async def get_donor_dashboard(donante_id: str) -> dict:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(DatabaseManager.executor, _sync_get_donor_dashboard, donante_id)
