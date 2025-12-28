<![CDATA["""
ARIA Configuration Management
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Application
    APP_NAME: str = "ARIA"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=4, env="WORKERS")
    
    # Security
    SECRET_KEY: str = Field(default="change-me-in-production", env="SECRET_KEY")
    ENCRYPTION_KEY: str = Field(default="change-me-32-byte-key-here!!", env="ENCRYPTION_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8081"],
        env="CORS_ORIGINS"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://aria:aria@localhost:5432/aria",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # LLM Configuration
    LLM_PROVIDER: str = Field(default="openai", env="LLM_PROVIDER")  # openai, anthropic, local
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    
    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    
    # Local LLM (Ollama, vLLM)
    LOCAL_LLM_ENDPOINT: Optional[str] = Field(default=None, env="LOCAL_LLM_ENDPOINT")
    LOCAL_LLM_MODEL: str = Field(default="llama2", env="LOCAL_LLM_MODEL")
    
    # External APIs
    # Uber
    UBER_CLIENT_ID: Optional[str] = Field(default=None, env="UBER_CLIENT_ID")
    UBER_CLIENT_SECRET: Optional[str] = Field(default=None, env="UBER_CLIENT_SECRET")
    UBER_SERVER_TOKEN: Optional[str] = Field(default=None, env="UBER_SERVER_TOKEN")
    
    # Google
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_SECRET")
    
    # TMDB
    TMDB_API_KEY: Optional[str] = Field(default=None, env="TMDB_API_KEY")
    
    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = Field(default=None, env="TWILIO_PHONE_NUMBER")
    
    # Web Automation
    BROWSER_HEADLESS: bool = Field(default=True, env="BROWSER_HEADLESS")
    BROWSERLESS_API_KEY: Optional[str] = Field(default=None, env="BROWSERLESS_API_KEY")
    BROWSERLESS_ENDPOINT: str = Field(
        default="wss://chrome.browserless.io",
        env="BROWSERLESS_ENDPOINT"
    )
    
    # Agent Configuration
    AGENT_MAX_ITERATIONS: int = 10
    AGENT_TIMEOUT_SECONDS: int = 300
    AGENT_MAX_RETRIES: int = 3
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "json"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    """
    return Settings()


# Global settings instance
settings = get_settings()


# Feature flags
class FeatureFlags:
    """
    Feature flags for gradual rollout.
    """
    
    # Enable web automation tier
    WEB_AUTOMATION_ENABLED: bool = True
    
    # Enable device control tier (Android A11y)
    DEVICE_CONTROL_ENABLED: bool = False
    
    # Enable PII sanitization
    PII_SANITIZATION_ENABLED: bool = True
    
    # Enable local LLM fallback
    LOCAL_LLM_FALLBACK_ENABLED: bool = False
    
    # Enable multi-agent orchestration
    MULTI_AGENT_ENABLED: bool = True
    
    # Enable real-time WebSocket updates
    WEBSOCKET_ENABLED: bool = True


features = FeatureFlags()
]]>
