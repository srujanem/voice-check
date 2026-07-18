"""
AI Shield — Configuration Module
Loads all settings from environment variables / .env file
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # App
    app_name: str = "AI-Shield-API"
    app_version: str = "1.0.0"
    debug: bool = True
    api_key: str = "ais_default_key"
    secret_key: str = "super-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite+aiosqlite:///./database/ai_shield.db"

    # Storage
    upload_dir: str = "./data/uploads"
    max_upload_size_mb: int = 50
    allowed_audio_extensions: str = ".wav,.mp3,.ogg,.flac,.m4a"
    allowed_image_extensions: str = ".jpg,.jpeg,.png,.webp,.bmp"

    # ML Models
    audio_model_path: str = "./trained_models/voice_shield_best.pt"
    image_model_path: str = "./trained_models/pixel_guard_best.pt"
    audio_confidence_threshold: float = 0.65
    image_confidence_threshold: float = 0.65

    # Training
    data_dir: str = "./data"
    logs_dir: str = "./logs"
    checkpoint_dir: str = "./trained_models"
    batch_size: int = 16
    learning_rate: float = 0.0001
    num_epochs: int = 20
    val_split: float = 0.2

    # GPU
    cuda_device: int = 0
    mixed_precision: bool = True
    num_workers: int = 4

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def allowed_audio_ext_list(self):
        return [e.strip() for e in self.allowed_audio_extensions.split(",")]

    @property
    def allowed_image_ext_list(self):
        return [e.strip() for e in self.allowed_image_extensions.split(",")]

    @property
    def max_upload_size_bytes(self):
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
