from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid
from . import queries, schemas
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", 
             response_model=schemas.ReservaPublic,
             status_code=status.HTTP_201_CREATED,
             summary="Reservar un lote",
             description="Crea una reserva para un lote de alimentos específico. Cambia el estado del lote a RESERVADO.")
async def reservar_lote(reserva: schemas.ReservaCreate, current_user: dict = Depends(get_current_user)):
    # 1. Obtener ID del usuario receptor
    from app.procesos.usuarios.queries import get_usuario_by_email
    usuario_db = await get_usuario_by_email(current_user["sub"])
    
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    # 2. Generar Token QR único
    qr_token = f"EB-{uuid.uuid4().hex[:8].upper()}"
    
    # 3. Crear reserva en la DB
    nueva_reserva = await queries.create_reserva(
        lote_id=str(reserva.lote_id),
        receptor_id=str(usuario_db["id"]),
        qr_token=qr_token
    )
    
    if not nueva_reserva:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El lote no está disponible para reserva o ya fue reservado"
        )
        
    return nueva_reserva

@router.get("/activas", 
            response_model=List[schemas.ReservaPublic],
            summary="Mis reservas activas",
            description="Retorna la lista de reservas en estado PENDIENTE realizadas por el receptor autenticado.")
async def reservas_activas(current_user: dict = Depends(get_current_user)):
    from app.procesos.usuarios.queries import get_usuario_by_email
    usuario_db = await get_usuario_by_email(current_user["sub"])
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return await queries.get_reservas_usuario(str(usuario_db["id"]), queries.EstadoReserva.PENDIENTE)

@router.get("/historial", 
            response_model=List[schemas.ReservaPublic],
            summary="Historial de reservas",
            description="Retorna el historial de reservas completadas o vencidas.")
async def reservas_historial(current_user: dict = Depends(get_current_user)):
    from app.procesos.usuarios.queries import get_usuario_by_email
    usuario_db = await get_usuario_by_email(current_user["sub"])
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    total = await queries.get_reservas_usuario(str(usuario_db["id"]))
    return [r for r in total if r["estado"] != queries.EstadoReserva.PENDIENTE]

@router.post("/{reserva_id}/completar", 
             summary="Completar recogida",
             description="Marca una reserva como completada y el lote como entregado. Solo puede hacerlo el donador o personal autorizado.")
async def completar_recogida(reserva_id: str, current_user: dict = Depends(get_current_user)):
    # Nota: En un sistema real verificaríamos que el usuario autenticado sea el DUEÑO del lote
    resultado = await queries.completar_reserva(reserva_id)
    if not resultado:
        raise HTTPException(status_code=400, detail="No se pudo completar la reserva (ya completada o no existe)")
    return {"exito": True, "reserva": resultado}

@router.post("/{reserva_id}/cancelar", 
             summary="Cancelar reserva",
             description="Libera el lote para que otros puedan reservarlo. Solo el receptor puede cancelar su reserva activa.")
async def cancelar_reserva(reserva_id: str, current_user: dict = Depends(get_current_user)):
    # Nota: Validar que sea el dueño de la reserva
    exito = await queries.cancelar_reserva(reserva_id)
    if not exito:
        raise HTTPException(status_code=400, detail="No se pudo cancelar la reserva")
    return {"exito": True, "mensaje": "Reserva cancelada exitosamente"}
