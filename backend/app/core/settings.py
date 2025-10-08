from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging
from typing import List, Optional, Dict, Any

class Settings(BaseSettings):
    # App configs - THÊM MỚI
    APP_NAME: str = "Social Automation API"
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    APP_ENV: str = "production"  # Thêm APP_ENV đã gây lỗi trước đó
    
    # Existing database and Redis configs
    DATABASE_URL: str = "postgresql+psycopg://thinh:123456@localhost:5433/social_automation"
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT settings
    JWT_SECRET: str = "change_this_super_secret_key" 
    JWT_ALG: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    JWT_REFRESH_EXPIRE_DAYS: int = 30  # Thêm mới

    # Media settings
    MEDIA_ROOT: str = "./uploads"
    
    # OAuth Settings
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    FACEBOOK_REDIRECT_URI: str = "http://localhost:8000/oauth/facebook/callback"
    
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    YOUTUBE_REDIRECT_URI: str = "http://localhost:8000/oauth/youtube/callback"
    
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    TIKTOK_REDIRECT_URI: str = "http://localhost:8000/oauth/tiktok/callback"
    
    # Timezone settings
    TIMEZONE_NAME: str = "Asia/Ho_Chi_Minh"
    
    # CORS & Logging - THÊM MỚI
    CORS_ORIGINS: str = "*"  # String thay vì List[str]
    LOG_LEVEL: str = "INFO"

    # Giữ nguyên cấu hình Pydantic
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore",
        case_sensitive=True
    )
    
    def validate_settings(self) -> None:
        """Kiểm tra các settings bắt buộc"""
        required = ["DATABASE_URL", "JWT_SECRET"]
        missing = [key for key in required if not getattr(self, key, None)]
        if missing:
            raise ValueError(f"Missing required settings: {', '.join(missing)}")

    # Thêm property để chuyển đổi từ string sang list khi cần
    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

# Singleton instance
_settings = None

@lru_cache
def get_settings() -> Settings:
    """Get settings singleton with error handling"""
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
            _settings.validate_settings()
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            # Fallback to defaults (already defined in the class)
            _settings = Settings()
            logging.warning("Using default settings - CHECK YOUR CONFIGURATION!")
    return _settings
