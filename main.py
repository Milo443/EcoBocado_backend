from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.bd_conections import DatabaseManager
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Inicializar pools de base de datos
    DatabaseManager.initialize_pools()
    yield
    # Shutdown: Cerrar pools
    DatabaseManager.shutdown()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para EcoBocado refactorizada",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "database": "connected"
    }

# Registro dinámico de routers
from app.procesos import routers
for router, prefix, tag in routers:
    app.include_router(router, prefix=f"/api/v1{prefix}", tags=[tag])