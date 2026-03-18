import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_file_encoding="utf-8"
    )
    
    # App Settings
    APP_NAME: str = "Endee RAG Platform"
    DEBUG: bool = False
    PORT: int = 5000
    APP_API_KEY: Optional[str] = None
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o-mini"
    
    # Endee Vector DB Settings
    ENDEE_URL: str = "http://localhost:8080"
    COLLECTION_NAME: str = "rag_docs"
    
    # RAG Settings
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 4

settings = Settings()
