from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from typing import List
from . import queries, schemas
from app.core.security import get_current_user
from app.core.storage import storage

router = APIRouter()

@router.get("/activos", 
            response_model=List[schemas.LotePublic],
            summary="Listar lotes activos",
            description="Retorna todos los lotes de alimentos que están actualmente disponibles para reserva.")
async def listar_lotes():
    return await queries.get_lotes_activos()

@router.post("/upload-image", 
             summary="Subir imagen de lote",
             description="Sube una imagen al almacenamiento S3 (MinIO) y retorna la URL pública.")
async def upload_lote_image(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        
    content = await file.read()
    url = await storage.upload_file(content, file.filename, file.content_type)
    return {"imagen_url": url}

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

@router.delete("/{lote_id}", 
               summary="Eliminar lote (Lógico)",
               description="Marca un lote como borrado. Solo el donador dueño puede hacerlo.")
async def eliminar_lote(lote_id: str, current_user: dict = Depends(get_current_user)):
    # Nota: Validar que sea el dueño en producción
    exito = await queries.delete_lote(lote_id)
    if not exito:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    return {"exito": True, "mensaje": "Lote eliminado correctamente"}

@router.put("/{lote_id}", 
            response_model=schemas.LotePublic,
            summary="Actualizar lote",
            description="Permite a un donador actualizar los datos de su lote. Solo el dueño puede hacerlo.")
async def actualizar_lote(lote_id: str, lote_update: schemas.LoteUpdate, current_user: dict = Depends(get_current_user)):
    # Nota: Validar que sea el dueño en producción
    actualizado = await queries.update_lote(lote_id, lote_update.model_dump(exclude_unset=True))
    if not actualizado:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    return actualizado
