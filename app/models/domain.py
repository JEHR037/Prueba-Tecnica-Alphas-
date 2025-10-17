from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class UserStatus(Enum):
    """Estados posibles de un usuario."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class User(BaseModel):
    """Modelo de dominio para representar un usuario."""
    id: Optional[int] = None
    email: EmailStr
    name: str
    status: UserStatus = UserStatus.ACTIVE
    age: int