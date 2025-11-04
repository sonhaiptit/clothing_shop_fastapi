"""Application configuration management."""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Database settings
    db_host: str = "localhost"
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "clothing_shop"
    db_charset: str = "utf8mb4"
    
    # Application settings
    secret_key: str = "change-this-secret-key-in-production"
    debug: bool = True
    
    # Server settings
    host: str = "127.0.0.1"
    port: int = 8000


settings = Settings()
