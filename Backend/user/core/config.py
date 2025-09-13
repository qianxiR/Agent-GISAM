"""
配置管理模块
统一管理所有系统配置
"""
from functools import lru_cache
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    app_name: str = Field(default="SuperMap GIS Platform", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=True, alias="DEBUG")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    
    # API 配置
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173", alias="CORS_ORIGINS")
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        # 保持原始字符串格式，在属性中处理转换
        return v
    
    @property
    def cors_origins_list(self) -> List[str]:
        """获取解析后的 CORS origins 列表"""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(',')]
        return self.cors_origins
    
    # 数据库配置
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="supermap_gis", alias="POSTGRES_DB")
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    # Redis 配置
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    
    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # SuperMap 配置
    supermap_base_url: str = Field(default="http://localhost:8090/iserver", alias="SUPERMAP_BASE_URL")
    supermap_server_url: str = Field(default="http://localhost:8090/iserver/services", alias="SUPERMAP_SERVER_URL")
    supermap_username: str = Field(default="admin", alias="SUPERMAP_USERNAME")
    supermap_password: str = Field(default="admin", alias="SUPERMAP_PASSWORD")

    # JWT 配置
    secret_key: str = Field(default="your-secret-key-here-change-in-production", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # 日志配置
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # DashScope / Vite 相关配置
    vite_dashscope_api_key: str = Field(default="your-dashscope-api-key-here", alias="VITE_DASHSCOPE_API_KEY")
    vite_dashscope_base_url: str = Field(default="https://dashscope.aliyuncs.com/api/v1", alias="VITE_DASHSCOPE_BASE_URL")
    vite_dashscope_model: str = Field(default="qwen-turbo", alias="VITE_DASHSCOPE_MODEL")
    vite_dashscope_temperature: float = Field(default=0.7, alias="VITE_DASHSCOPE_TEMPERATURE")
    vite_dashscope_max_tokens: int = Field(default=2000, alias="VITE_DASHSCOPE_MAX_TOKENS")
    
    # RAG PostgreSQL 配置
    rag_postgres_host: str = Field(default="localhost", alias="RAG_POSTGRES_HOST")
    rag_postgres_port: int = Field(default=5432, alias="RAG_POSTGRES_PORT")
    rag_postgres_user: str = Field(default="postgres", alias="RAG_POSTGRES_USER")
    rag_postgres_password: str = Field(default="postgres", alias="RAG_POSTGRES_PASSWORD")
    rag_postgres_db: str = Field(default="rag_database", alias="RAG_POSTGRES_DB")
    rag_postgres_schema: str = Field(default="public", alias="RAG_POSTGRES_SCHEMA")
    rag_postgres_table: str = Field(default="documents", alias="RAG_POSTGRES_TABLE")
    rag_postgres_text_columns: str = Field(default="content,title,summary", alias="RAG_POSTGRES_TEXT_COLUMNS")
    
    @property
    def rag_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.rag_postgres_user}:{self.rag_postgres_password}@{self.rag_postgres_host}:{self.rag_postgres_port}/{self.rag_postgres_db}"
    
    model_config = SettingsConfigDict(
        env_file="Backend/.env",
        case_sensitive=False,
    )


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 全局配置实例
settings = get_settings()