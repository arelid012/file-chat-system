# backend/src/core/config.py
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings  # CHANGED THIS LINE!
from pydantic import Field  # Keep this for field configuration

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
    
    # Changed from class Config to model_config
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }

settings = Settings()