from fastapi import APIRouter, Depends, HTTPException
from . import queries
from app.core.security import get_current_user

router = APIRouter()

@router.get("/global", 
            summary="Impacto Histórico Global",
            description="Retorna las métricas acumuladas de impacto social y ambiental de toda la plataforma.")
async def impacto_global():
    return await queries.get_global_impact()

@router.get("/dashboard-donante", 
            summary="Métricas de Donante",
            description="Retorna las estadísticas personalizadas para el panel principal del donador.")
async def dashboard_donante(current_user: dict = Depends(get_current_user)):
    from app.procesos.usuarios.queries import get_usuario_by_email
    usuario_db = await get_usuario_by_email(current_user["sub"])
    
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    return await queries.get_donor_dashboard(str(usuario_db["id"]))
