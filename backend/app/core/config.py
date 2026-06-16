from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduBot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "edubot"
    POSTGRES_PASSWORD: str = "secure_password"
    POSTGRES_DB: str = "edubot_db"
    DATABASE_URL: str = None
    
    @property
    def async_database_url(self) -> str:
        return self.DATABASE_URL or f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "edubot_logs"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "changeme_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # NLP
    NLP_MODEL_PATH: str = "./models/nlp_model"
    NLP_CONFIDENCE_THRESHOLD: float = 0.9
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Performance
    MAX_CONCURRENT_USERS: int = 500
    RESPONSE_TIMEOUT_SECONDS: int = 2
    
    # GROQ API
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str | None = None

    # Twilio API
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_WHATSAPP_NUMBER: str | None = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()