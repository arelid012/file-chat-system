# backend/src/core/config.py
import os
from pathlib import Path
from typing import List
from pydantic import BaseSettings  # DIRECT IMPORT - NO pydantic-settings!

class Settings(BaseSettings):
    # Server
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:3000"    
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "file_chat_db"
    
    # File Processing
    MAX_FILE_SIZE_MB: int = 50
    UPLOAD_DIR: str = "uploads"
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "phi:latest"
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    UPLOAD_PATH: Path = BASE_DIR / UPLOAD_DIR
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()