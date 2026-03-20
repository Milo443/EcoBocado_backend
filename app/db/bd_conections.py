import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base
from concurrent.futures import ThreadPoolExecutor
from typing import Dict
import logging

from app.core.config import settings
from .database import db_settings
from .db_configs import DATABASES

# Logger para la base de datos
logger = logging.getLogger("app.db")

Base = declarative_base()

class DatabaseManager:
    _engines: Dict[str, sa.Engine] = {}
    executor: ThreadPoolExecutor = None
    
    @classmethod
    def initialize_pools(cls):
        """Inicializa los pools de conexiones y el executor global."""
        if cls.executor is None:
            cls.executor = ThreadPoolExecutor(
                max_workers=settings.DB_THREAD_WORKERS,
                thread_name_prefix="DBWorker"
            )
            logger.info(f"ThreadPoolExecutor inicializado con {settings.DB_THREAD_WORKERS} workers")

        for db_id, config in DATABASES.items():
            if not config.get("enabled", False):
                continue
            
            try:
                engine = sa.create_engine(
                    config["url"],
                    pool_size=db_settings.DB_POOL_SIZE,
                    max_overflow=db_settings.DB_MAX_OVERFLOW,
                    pool_recycle=db_settings.DB_POOL_RECYCLE,
                    echo=False
                )
                cls._engines[db_id] = engine
                logger.info(f"Pool para {db_id} ({config['name']}) inicializado")
            except Exception as e:
                logger.error(f"Error inicializando pool para {db_id}: {str(e)}")

    @classmethod
    def _get_engine(cls, db_id: str) -> sa.Engine:
        """Retorna el engine solicitado."""
        if db_id not in cls._engines:
            raise ValueError(f"Base de datos {db_id} no configurada o habilitada")
        return cls._engines[db_id]

    @classmethod
    def get_schema(cls, db_id: str) -> str:
        """Retorna el schema configurado para la base de datos."""
        return DATABASES[db_id].get("schema", "public")

    @classmethod
    def shutdown(cls):
        """Cierra todos los pools y el executor."""
        if cls.executor:
            cls.executor.shutdown(wait=True)
        for engine in cls._engines.values():
            engine.dispose()
        logger.info("DatabaseManager apagado")
