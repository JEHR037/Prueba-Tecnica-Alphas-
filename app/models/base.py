from abc import ABC, abstractmethod
from typing import Optional
from app.models.domain import User


class UserRepository(ABC):
    """Interfaz abstracta para el repositorio de usuarios."""
    
    @abstractmethod
    def save(self, user: User) -> User:
        """Guarda usuario y retorna con ID asignado"""
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuario por ID"""
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Busca usuario por email"""
        pass

