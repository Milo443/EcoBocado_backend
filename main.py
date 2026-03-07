
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Inicializamos la aplicación FastAPI con metadatos del proyecto
app = FastAPI(
    title="EcoBocado API",
    description="API para el MVP de EcoBocado: Rescate de Alimentos en Tiempo Real",
    version="1.0.0",
    docs_url="/docs", # Interfaz Swagger autogenerada
    redoc_url="/redoc" # Interfaz ReDoc
)

# Configuración de CORS (Cross-Origin Resource Sharing)
# Esto es vital porque nuestro frontend estará en React (Vite) 
# y correrá en un puerto distinto (ej. localhost:5173) durante el desarrollo.
origenes_permitidos = [
    "http://localhost:5173", # Puerto por defecto de Vite (React)
    "http://127.0.0.1:5173",
    # "https://midominio.com", # Aquí agregaremos el dominio de producción luego
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"], # Permite todos los headers (incluyendo Authorization para JWT)
)

# Endpoint de prueba (Health Check)
@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "proyecto": "EcoBocado: Rescate de Alimentos en Tiempo Real",
        "mensaje": "Servidor FastAPI funcionando correctamente bajo arquitectura DDD."
    }

# Aquí es donde, más adelante, importaremos y registraremos nuestros Routers de la capa 'api/'
# ej: app.include_router(usuarios_router, prefix="/api/v1/usuarios")
# ej: app.include_router(lotes_router, prefix="/api/v1/lotes")