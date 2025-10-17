from fastapi import APIRouter, status
from pydantic import BaseModel, EmailStr

from app.models.domain import User, UserStatus
from app.models.exception import (
    UserNotFoundException,
    DuplicateEmailException,
    InvalidAgeException,
    InvalidUserNameException,
    AppBaseException
)
from app.services.logger import get_logger

logger = get_logger(__name__)

# Crear el router principal
router = APIRouter()


# ==================== Modelos de Request/Response ====================

class UserCreateRequest(BaseModel):
    """Modelo para crear un nuevo usuario."""
    email: EmailStr
    name: str
    age: int
    status: UserStatus = UserStatus.ACTIVE
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@ejemplo.com",
                "name": "Juan Pérez",
                "age": 25,
                "status": "active"
            }
        }


class UserResponse(BaseModel):
    """Modelo de respuesta para usuarios."""
    id: int
    email: EmailStr
    name: str
    age: int
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "usuario@ejemplo.com",
                "name": "Juan Pérez",
                "age": 25,
                "status": "active"
            }
        }


class ErrorResponse(BaseModel):
    """Modelo de respuesta para errores."""
    error: str
    detail: str


class EmailCheckResponse(BaseModel):
    """Modelo de respuesta para verificación de email."""
    email: str
    exists: bool
    available: bool


class HealthCheckResponse(BaseModel):
    """Modelo de respuesta para health check."""
    status: str
    service: str
    repository: str
    version: str


# ==================== Dependency ====================

# Variable global que será inyectada desde main.py
_user_service = None


def set_user_service(service):
    """Configura el servicio de usuarios para ser usado en las rutas."""
    global _user_service
    _user_service = service


def get_user_service():
    """Obtiene la instancia del servicio de usuarios."""
    if _user_service is None:
        raise RuntimeError("UserService no ha sido inicializado")
    return _user_service


# ==================== Endpoints de Health ====================

@router.get(
    "/",
    tags=["Health"],
    summary="Endpoint raíz",
    description="Endpoint de prueba para verificar que la API está funcionando."
)
async def root():
    """Endpoint de prueba para verificar que la API está funcionando."""
    logger.info("Handling root endpoint")
    return {
        "message": "Alphas User Management API is running",
        "version": "1.0.0",
        "status": "healthy"
    }


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["Health"],
    summary="Health Check",
    description="Endpoint de verificación de salud de la API."
)
async def health_check():
    """Endpoint de verificación de salud de la API."""
    logger.debug("Health check solicitado")
    return {
        "status": "healthy",
        "service": "User Management API",
        "repository": "SQLAlchemy (In-Memory)",
        "version": "1.0.0"
    }


# ==================== Endpoints de Usuarios ====================

@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
    summary="Crear usuario",
    description="Crea un nuevo usuario en el sistema.",
    responses={
        201: {"description": "Usuario creado exitosamente"},
        400: {"description": "Datos inválidos (edad menor a 18 o nombre vacío)"},
        409: {"description": "Email duplicado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def create_user(user_data: UserCreateRequest):
    """
    Crea un nuevo usuario en el sistema.
    
    Validaciones:
    - **email**: Email único del usuario (formato válido)
    - **name**: Nombre completo del usuario (no puede estar vacío o solo espacios)
    - **age**: Edad del usuario (debe ser >= 18 años)
    - **status**: Estado del usuario (active o inactive, por defecto active)
    
    Returns:
        UserResponse: Usuario creado con ID asignado
        
    Raises:
        InvalidAgeException: Si la edad es menor a 18 años
        InvalidUserNameException: Si el nombre está vacío o solo contiene espacios
        DuplicateEmailException: Si el email ya existe
    """
    logger.info(f"POST /users - Creando usuario con email: {user_data.email}")
    
    try:
        user_service = get_user_service()
        
        # Crear usuario usando el servicio
        user = user_service.create_user(
            email=user_data.email,
            name=user_data.name,
            age=user_data.age,
            status=user_data.status
        )
        
        logger.info(f"Usuario creado exitosamente con ID: {user.id}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            age=user.age,
            status=user.status.value
        )
    except (InvalidAgeException, InvalidUserNameException, DuplicateEmailException, AppBaseException):
        raise


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Obtener usuario por ID",
    description="Obtiene un usuario específico por su ID.",
    responses={
        200: {"description": "Usuario encontrado"},
        404: {"description": "Usuario no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_user(user_id: int):
    """
    Obtiene un usuario por su ID.
    
    Args:
        user_id: ID del usuario a buscar
        
    Returns:
        UserResponse: Información del usuario
        
    Raises:
        UserNotFoundException: Si el usuario no existe
    """
    logger.info(f"GET /users/{user_id} - Buscando usuario")
    
    try:
        user_service = get_user_service()
        user = user_service.get_user_by_id(user_id)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            age=user.age,
            status=user.status.value
        )
    except (UserNotFoundException, AppBaseException):
        raise


@router.get(
    "/users/email/{email}",
    response_model=UserResponse,
    tags=["Users"],
    summary="Obtener usuario por email",
    description="Obtiene un usuario específico por su email.",
    responses={
        200: {"description": "Usuario encontrado"},
        404: {"description": "Usuario no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def get_user_by_email(email: str):
    """
    Obtiene un usuario por su email.
    
    Args:
        email: Email del usuario a buscar
        
    Returns:
        UserResponse: Información del usuario
        
    Raises:
        UserNotFoundException: Si el usuario no existe
    """
    logger.info(f"GET /users/email/{email} - Buscando usuario por email")
    
    try:
        user_service = get_user_service()
        user_dict = user_service.get_user_by_email(email)
        
        return UserResponse(
            id=user_dict["id"],
            email=user_dict["email"],
            name=user_dict["name"],
            age=user_dict["age"],
            status=user_dict["status"]
        )
    except (UserNotFoundException, AppBaseException):
        raise


@router.get(
    "/users/check-email/{email}",
    response_model=EmailCheckResponse,
    tags=["Users"],
    summary="Verificar disponibilidad de email",
    description="Verifica si un email ya existe en el sistema.",
    responses={
        200: {"description": "Verificación exitosa"},
        500: {"description": "Error interno del servidor"}
    }
)
async def check_email_exists(email: str):
    """
    Verifica si un email ya existe en el sistema.
    
    Args:
        email: Email a verificar
        
    Returns:
        EmailCheckResponse: Estado de existencia y disponibilidad del email
    """
    logger.info(f"GET /users/check-email/{email} - Verificando existencia de email")
    
    try:
        user_service = get_user_service()
        exists = user_service.email_exists(email)
        
        return EmailCheckResponse(
            email=email,
            exists=exists,
            available=not exists
        )
    except AppBaseException:
        raise

