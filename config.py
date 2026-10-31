from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "乙H OFFICIAL"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/zh_official"
    JWT_SECRET: str = "CHANGE_THIS_TO_A_SUPER_SECURE_RANDOM_SECRET_KEY_64_CHARS"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ADMIN_SECRET_KEY: str = "ADMIN_SECURE_KEY_乙H_2026"
    
    # External Token Exchange Service Gateway
    EXTERNAL_TOKEN_GATEWAY_URL: Optional[str] = "https://api.gateway.provider.com/v1"
    EXTERNAL_API_KEY: Optional[str] = "YOUR_EXTERNAL_GATEWAY_API_KEY"
    
    # Telegram Integration
    TELEGRAM_BOT_TOKEN: Optional[str] = ""
    TELEGRAM_ADMIN_CHAT_ID: Optional[str] = ""

    # Security & CORS
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()