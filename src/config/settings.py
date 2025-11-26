import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Healthy RAG"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "YOUR_SECRET_KEY_HERE_PLEASE_CHANGE"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Database
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/healthy.db"
    
    # AI
    DEEP_SEEK_API_KEY: Optional[str] = Field(default=None, alias="DEEP_SEEK") 
    DEEP_SEEK_MODEL_REASONER: str = "deepseek-reasoner"
    DEEP_SEEK_TIMEOUT: int = 300

    # Gemini (GRSAI)
    GEMINI_API_KEY: Optional[str] = Field(default=None, alias="GRSAI_KEY")
    GEMINI_BASE_URL: str = "https://grsai.dakka.com.cn/v1"
    GEMINI_MODEL: str = "gemini-3-pro"
    GEMINI_TIMEOUT: int = 300

    # Volcengine (火山引擎)
    # 优先匹配 ARK_API_KEY
    VOLC_API_KEY: Optional[str] = Field(default=None, validation_alias="ARK_API_KEY")
    VOLC_EMBEDDING_MODEL: str = "ep-m-20251125184146-lsgvz"
    VOLC_API_BASE: str = "https://ark.cn-beijing.volces.com/api/v3"

    # Weaviate
    WEAVIATE_URL: str = "http://localhost:8080"
    WEAVIATE_API_KEY: Optional[str] = None

    # Aliyun OSS
    OSS_ACCESS_KEY_ID: Optional[str] = None
    OSS_ACCESS_KEY_SECRET: Optional[str] = None
    OSS_BUCKET_NAME: Optional[str] = None
    OSS_ENDPOINT: str = "https://oss-cn-shanghai.aliyuncs.com"
    OSS_PUBLIC_READ: bool = True

    class Config:
        # 读取 .env
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"
        populate_by_name = True 

settings = Settings()
