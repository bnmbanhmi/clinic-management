from pydantic_settings import BaseSettings, SettingsConfigDict # Ensure SettingsConfigDict is imported if you are on Pydantic V2
# If you are on Pydantic V1, it might just be:
# from pydantic import BaseSettings
import os
from typing import Optional

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Email settings
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ("true", "1", "t")
MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() in ("true", "1", "t")
MAIL_FROM = os.getenv("MAIL_FROM")

# Frontend URL for constructing password reset links
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    GOOGLE_API_KEY: str

    # Email settings
    MAIL_SERVER: Optional[str] = MAIL_SERVER
    MAIL_PORT: int = MAIL_PORT
    MAIL_USERNAME: Optional[str] = MAIL_USERNAME
    MAIL_PASSWORD: Optional[str] = MAIL_PASSWORD
    MAIL_USE_TLS: bool = MAIL_USE_TLS
    MAIL_USE_SSL: bool = MAIL_USE_SSL
    MAIL_FROM: Optional[str] = MAIL_FROM

    # Frontend URL for constructing password reset links
    FRONTEND_URL: str = FRONTEND_URL

    # For Pydantic V2
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

    # For Pydantic V1, you would use a nested Config class:
    # class Config:
    #     env_file = ".env"

settings = Settings()