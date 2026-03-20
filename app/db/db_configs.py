from .database import db_settings

_POSTGRES_URL = f"postgresql://{db_settings.POSTGRES_USER}:{db_settings.POSTGRES_PASSWORD}@{db_settings.POSTGRES_SERVER}:{db_settings.POSTGRES_PORT}/{db_settings.POSTGRES_DB}"

DATABASES = {
    "postgres_ecobocado": {
        "type": "postgresql",
        "url": _POSTGRES_URL,
        "schema": "public",
        "name": "EcoBocado PostgreSQL",
        "enabled": True
    }
}
