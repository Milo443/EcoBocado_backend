import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Agregar la raíz del proyecto al PYTHONPATH
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# Importar Base y modelos
from app.db.bd_conections import Base, DatabaseManager
from app.db.db_configs import DATABASES

# Importar modelos para que sean detectados por autogenerate
from app.procesos.usuarios.models import UsuarioORM
from app.procesos.lotes.models import LoteORM
from app.procesos.reservas.models import ReservaORM

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        return name in target_metadata.tables
    return True

def get_url():
    return DATABASES["postgres_ecobocado"]["url"]

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Usar la URL de configuración dinámica
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
