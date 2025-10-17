from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    Las variables pueden ser sobrescritas mediante variables de entorno.
    """
    
    # Información de la aplicación
    APP_NAME: str = "Alphas User Management API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API para gestión de usuarios con patrón Repository"
    
    # Configuración de la base de datos
    DATABASE_URL: str = "sqlite:///:memory:"
    
    # Configuración de logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: str = "app.log"
    
    # Configuración de edad mínima
    MIN_USER_AGE: int = 18
    
    # Configuración del servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # CORS
    ALLOW_ORIGINS: list = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list = ["*"]
    ALLOW_HEADERS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()

