from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from . import queries, schemas
from app.core.security import get_current_user

router = APIRouter()

@router.get("/activos", 
            response_model=List[schemas.LotePublic],
            summary="Listar lotes activos",
            description="Retorna todos los lotes de alimentos que están actualmente disponibles para reserva.")
async def listar_lotes():
    return await queries.get_lotes_activos()

@router.post("/", 
             response_model=schemas.LotePublic,
             status_code=status.HTTP_201_CREATED,
             summary="Publicar nuevo lote",
             description="Permite a un donador publicar un nuevo lote de alimentos. Requiere autenticación.")
async def publicar_lote(lote: schemas.LoteCreate, current_user: dict = Depends(get_current_user)):
    # Verificar que el usuario sea DONOR
    if current_user.get("role") != "DONOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los donadores pueden publicar lotes"
        )
    
    # Obtener el ID del usuario desde la DB usando el email (sub)
    from app.procesos.usuarios.queries import get_usuario_by_email
    usuario_db = await get_usuario_by_email(current_user["sub"])
    
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    return await queries.create_lote(lote.model_dump(), str(usuario_db["id"]))

@router.get("/mis-lotes", 
            response_model=List[schemas.LotePublic],
            summary="Mis publicaciones",
            description="Retorna la lista de lotes publicados por el donador autenticado.")
async def mis_lotes(current_user: dict = Depends(get_current_user)):
    from app.procesos.usuarios.queries import get_usuario_by_email
    usuario_db = await get_usuario_by_email(current_user["sub"])
    
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    return await queries.get_lotes_by_donante(str(usuario_db["id"]))
