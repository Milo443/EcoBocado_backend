# Importamos modelos PRIMERO para asegurar que SQLAlchemy registre las relaciones
from .usuarios.models import UsuarioORM, OTPRecord
from .lotes.models import LoteORM
from .reservas.models import ReservaORM

from .usuarios.router import router as usuarios_router
from .lotes.router import router as lotes_router
from .reservas.router import router as reservas_router
from .impacto.router import router as impacto_router

# Exportamos para fácil importación en main.py
routers = [
    (usuarios_router, "/usuarios", "Usuarios"),
    (lotes_router, "/lotes", "Lotes"),
    (reservas_router, "/reservas", "Reservas"),
    (impacto_router, "/impacto", "Impacto"),
]
