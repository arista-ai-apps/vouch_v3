import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Arista AI - SV-CIE"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-poc-development")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    STORAGE_DIR: str = os.path.join(os.getcwd(), "storage")
    
    class Config:
        case_sensitive = True

settings = Settings()
