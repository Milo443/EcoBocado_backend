from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from src.infrastructure.config import settings

# 1. Crear el Motor Asíncrono (Engine)
# echo=True imprimirá las consultas SQL en la consola (útil para desarrollo)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
    pool_size=5, # Mantiene 5 conexiones abiertas listas para usar
    max_overflow=10 # Permite hasta 10 conexiones extra en picos de tráfico
)

# 2. Configurar la Fábrica de Sesiones
# class_=AsyncSession garantiza que usemos la API asíncrona de SQLAlchemy
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 3. Base Declarativa
# Todos nuestros modelos ORM (tablas) heredarán de esta clase
Base = declarative_base()

# 4. Dependencia para FastAPI (Inyección de Dependencias)
# Esta función asíncrona la usaremos en nuestros endpoints para obtener una sesión
# y nos aseguramos de cerrarla (yield) cuando la petición termine, pase lo que pase.
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()