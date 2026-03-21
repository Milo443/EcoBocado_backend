from minio import Minio
from app.core.config import settings
import io
import uuid
from datetime import datetime

class MinioStorage:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MinioStorage, cls).__new__(cls)
            # Inicializar cliente MinIO
            # Eliminamos el prefijo https:// para el endpoint si existe
            endpoint = settings.MINIO_ENDPOINT.replace("https://", "").replace("http://", "")
            
            cls._instance.client = Minio(
                endpoint,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_ENDPOINT.startswith("https")
            )
            cls._instance.bucket_name = settings.MINIO_BUCKET_NAME
            
            # Asegurar que el bucket existe
            if not cls._instance.client.bucket_exists(cls._instance.bucket_name):
                cls._instance.client.make_bucket(cls._instance.bucket_name)
            
            # Configurar política de lectura pública para el bucket
            import json
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                        "Resource": [f"arn:aws:s3:::{cls._instance.bucket_name}"]
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{cls._instance.bucket_name}/*"]
                    }
                ]
            }
            cls._instance.client.set_bucket_policy(cls._instance.bucket_name, json.dumps(policy))
                
        return cls._instance

    async def upload_file(self, file_data: bytes, filename: str, content_type: str) -> str:
        # Generar nombre único
        ext = filename.split('.')[-1]
        unique_name = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        
        # Subir a MinIO
        file_stream = io.BytesIO(file_data)
        self.client.put_object(
            self.bucket_name,
            unique_name,
            file_stream,
            len(file_data),
            content_type=content_type
        )
        
        # Retornar URL pública (asumiendo que el bucket es público o vía proxy)
        return f"{settings.MINIO_ENDPOINT}/{self.bucket_name}/{unique_name}"

storage = MinioStorage()
