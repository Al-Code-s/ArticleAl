"""
应用配置
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    PROJECT_NAME: str = "ArticleAI"
    APP_NAME: str = "ArticleAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    PORT: int = 3000

    # 数据库
    DATABASE_URL: str
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    # AI配置
    DEFAULT_AI_PROVIDER: str = "claude"
    DEFAULT_AI_MODEL: str = "claude-3-sonnet-20240229"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # 知网
    CNKI_API_URL: str = ""
    CNKI_API_KEY: str = ""

    # 文件
    UPLOAD_DIR: str = "./uploads"
    EXPORT_DIR: str = "./exports"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # 日志
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MESSAGE_QUEUE_SIZE: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    def get_cors_origins(self) -> List[str]:
        """获取CORS origins列表"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS


settings = Settings()
