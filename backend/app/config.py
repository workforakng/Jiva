import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    app_name: str = "Jīva Health API"
    version: str = "1.0.0"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:19006"]
    
    # Firebase
    firebase_project_id: str
    google_application_credentials: str
    
    # Google Cloud
    google_cloud_project_id: str
    google_cloud_storage_bucket: str
    
    # Security
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    
    # OCR & NLP
    spacy_model: str = "en_core_web_sm"
    ocr_confidence_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
