"""Core configuration using Pydantic Settings for environment variables."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Base10 API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days (offline-first needs longer tokens)
    
    # CORS - Allow web app and mobile app
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5000"]
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return self.BACKEND_CORS_ORIGINS
    
    # SMS (Phase 3)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Storage & CDN
    STORAGE_BACKEND: str = "local"  # 's3', 'minio', or 'local'
    S3_BUCKET_NAME: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_ENDPOINT_URL: str = ""  # For MinIO self-hosted
    S3_CDN_DOMAIN: str = ""  # CloudFront domain
    LOCAL_STORAGE_PATH: str = "./media"
    
    # Cloudinary (Image Optimization)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    
    # Analytics
    POSTHOG_API_KEY: str = ""
    POSTHOG_HOST: str = "https://app.posthog.com"
    TIMESCALE_URL: str = ""  # PostgreSQL with TimescaleDB extension
    
    # Email (Phase 2)
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = ""
    
    # Push Notifications (Phase 2)
    FIREBASE_CREDENTIALS_PATH: str = ""
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
