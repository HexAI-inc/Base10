"""Core configuration using Pydantic Settings for environment variables."""
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Base10 API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    POSTGRES_USER: str = "base10"
    POSTGRES_PASSWORD: str = "base10_password"
    POSTGRES_DB: str = "base10_db"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days (offline-first needs longer tokens)
    
    # CORS - Allow web app and mobile app
    BACKEND_CORS_ORIGINS: str = '["http://localhost:3000", "http://localhost:5000", "https://stingray-app-x7lzo.ondigitalocean.app", "https://base10.gm", "https://www.base10.gm"]'
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from JSON string or return default."""
        try:
            if isinstance(self.BACKEND_CORS_ORIGINS, str):
                origins = json.loads(self.BACKEND_CORS_ORIGINS)
                # Remove wildcard if it exists (not allowed with credentials)
                if "*" in origins:
                    origins.remove("*")
                    # If only "*" was present, add default origins
                    if not origins:
                        origins = ["http://localhost:3000", "http://localhost:5000", "https://stingray-app-x7lzo.ondigitalocean.app", "https://base10.gm", "https://www.base10.gm"]
                # Always allow localhost for development
                if "http://localhost:3000" not in origins:
                    origins.append("http://localhost:3000")
                return origins
            return self.BACKEND_CORS_ORIGINS
        except:
            return ["http://localhost:3000", "http://localhost:5000", "https://stingray-app-x7lzo.ondigitalocean.app", "https://base10.gm", "https://www.base10.gm"]
    
    # SMS (Phase 3)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Storage & CDN
    STORAGE_BACKEND: str = "s3"  # 's3', 'minio', or 'local'
    SPACES_BUCKET_NAME: str = ""
    SPACES_ACCESS_KEY_ID: str = ""
    SPACES_SECRET_ACCESS_KEY: str = ""
    SPACES_REGION: str = "lon1"
    SPACES_ENDPOINT_URL: str = ""  # e.g., https://lon1.digitaloceanspaces.com
    SPACES_CDN_DOMAIN: str = ""    # e.g., base10-storage-bucket.lon1.cdn.digitaloceanspaces.com
    LOCAL_STORAGE_PATH: str = "./media"
    
    # Cloudinary (Image Optimization)
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    
    # Analytics
    POSTHOG_API_KEY: str = ""
    POSTHOG_HOST: str = "https://app.posthog.com"
    TIMESCALE_URL: str = ""  # PostgreSQL with TimescaleDB extension
    
    # Email Service (Resend)
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "Base10 <noreply@base10.app>"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Push Notifications (Phase 2)
    FIREBASE_CREDENTIALS_PATH: str = ""
    
    # AI
    GOOGLE_API_KEY: str = ""
    AI_MODEL_NAME: str = "gemini-pro"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
