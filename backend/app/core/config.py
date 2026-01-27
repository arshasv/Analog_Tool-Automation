"""
Core configuration for the AI-Driven Sky130 ASIC Platform
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "AI-Driven Sky130 ASIC Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/platform.db"
    
    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # PDK Configuration
    PDK_ROOT: str = os.getenv("PDK_ROOT", "/opt/sky130_pdk")
    PDK_NAME: str = "sky130A"
    SKY130_PDK: str = os.getenv("SKY130_PDK", "/opt/sky130_pdk/sky130A")
    
    # EDA Tools Paths
    NGSPICE_BIN: str = "/usr/local/bin/ngspice"
    MAGIC_BIN: str = "/usr/local/bin/magic"
    NETGEN_BIN: str = "/usr/local/bin/netgen"
    KLAYOUT_BIN: str = "/opt/klayout-src/bin-release/klayout"
    
    # Working Directories
    WORK_DIR: str = "./data/designs"
    RESULTS_DIR: str = "./data/results"
    CACHE_DIR: str = "./data/cache"
    
    # Simulation Settings
    MAX_SIMULATION_TIME: int = 300  # seconds
    SIMULATION_TIMEOUT: int = 60
    
    # AI Engine Settings
    AI_ENABLED: bool = True
    MAX_OPTIMIZATION_ITERATIONS: int = 100
    OPTIMIZATION_TIMEOUT: int = 3600  # 1 hour
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/platform.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
