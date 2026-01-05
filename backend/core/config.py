from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True
    )
    
    PROJECT_NAME: str = "SahihAksara API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sahih_aksara.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sahihaksara_secret_key_9912837_replace_this")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Payment Gateway (UnikaPay)
    UNIKAPAY_API_KEY: str = os.getenv("UNIKAPAY_API_KEY", "")
    UNIKAPAY_BASE_URL: str = os.getenv("UNIKAPAY_BASE_URL", "https://unikapay.unikarta.ac.id")

    # Public Application URL
    APP_URL: str = os.getenv("APP_URL", "https://sahihaksara.id")

settings = Settings()
