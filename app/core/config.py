from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "EcoBocado API"
    ENVIRONMENT: str = "development"
    
    # Seguridad
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # MinIO
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str
    
    # EmailJS
    EMAILJS_SERVICE_ID: str | None = None
    EMAILJS_TEMPLATE_ID: str | None = None
    EMAILJS_PUBLIC_KEY: str | None = None
    EMAILJS_PRIVATE_KEY: str | None = None
    
    # OTP Settings
    OTP_EXPIRY_MINUTES: int = 10
    
    # Thread Pool
    DB_THREAD_WORKERS: int = 10
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
