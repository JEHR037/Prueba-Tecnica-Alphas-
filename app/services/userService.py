from typing import Optional, List

from app.models.domain import User, UserStatus
from app.models.base import UserRepository
from app.models.exception import (
    UserNotFoundException,
    DuplicateEmailException,
    InvalidAgeException,
    InvalidUserNameException,
    AppBaseException
)
from app.services.logger import get_logger, log_exception

logger = get_logger(__name__)


class UserService:
    """
    Servicio de negocio para gestión de usuarios.
    Implementa la lógica de negocio y utiliza el patrón Repository para persistencia.
    """
    
    def __init__(self, user_repository: UserRepository):
        """
        Inicializa el servicio con un repositorio de usuarios.
        
        Args:
            user_repository: Implementación del repositorio de usuarios
        """
        self.user_repository = user_repository
        logger.info("UserService inicializado correctamente")

    def create_user(self, email: str, name: str, age: int, status: UserStatus = UserStatus.ACTIVE) -> User:
        """
        Crea un nuevo usuario en el sistema.
        
        Args:
            email: Email del usuario (debe ser único)
            name: Nombre del usuario
            age: Edad del usuario (debe ser >= 18)
            status: Estado del usuario (por defecto ACTIVE)
            
        Returns:
            User: Usuario creado con ID asignado
            
        Raises:
            InvalidAgeException: Si la edad es menor a 18 años
            InvalidUserNameException: Si el nombre está vacío o solo contiene espacios
            DuplicateEmailException: Si el email ya existe en la base de datos
        """
        try:
            logger.info(f"Intentando crear usuario con email: {email}")
            
            # Crear objeto User
            new_user = User(
                email=email,
                name=name,
                age=age,
                status=status
            )
            
            # Guardar en el repositorio
            saved_user = self.user_repository.save(new_user)
            
            logger.info(f"Usuario creado exitosamente con ID: {saved_user.id}")
            return saved_user
            
        except (InvalidAgeException, InvalidUserNameException, DuplicateEmailException) as e:
            logger.error(f"Error de validación al crear usuario: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al crear usuario: {str(e)}")
            raise AppBaseException(f"Error al crear usuario: {str(e)}")

    def get_user_by_id(self, user_id: int) -> User:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: ID del usuario a buscar
            
        Returns:
            User: Usuario encontrado
            
        Raises:
            UserNotFoundException: Si el usuario no existe
        """
        try:
            logger.info(f"Buscando usuario con ID: {user_id}")
            user = self.user_repository.find_by_id(user_id)
            logger.info(f"Usuario encontrado: {user.email}")
            return user
            
        except UserNotFoundException as e:
            logger.error(f"Usuario con ID {user_id} no encontrado")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al buscar usuario por ID: {str(e)}")
            raise AppBaseException(f"Error al buscar usuario: {str(e)}")

    def get_user_by_email(self, email: str) -> dict:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario a buscar
            
        Returns:
            dict: Datos del usuario en formato diccionario
            
        Raises:
            UserNotFoundException: Si el usuario no existe
        """
        try:
            logger.info(f"Buscando usuario con email: {email}")
            user_dict = self.user_repository.get_user_by_email(email)
            
            if 'error' in user_dict:
                logger.error(f"Error al buscar usuario por email: {user_dict['error']}")
                raise UserNotFoundException(user_dict['error'])
            
            logger.info(f"Usuario encontrado con email: {email}")
            return user_dict
            
        except UserNotFoundException as e:
            logger.error(f"Usuario con email {email} no encontrado")
            raise
        except Exception as e:
            logger.error(f"Error inesperado al buscar usuario por email: {str(e)}")
            raise AppBaseException(f"Error al buscar usuario: {str(e)}")

    def validate_user_age(self, age: int) -> bool:
        """
        Valida que la edad del usuario sea válida (>= 18 años).
        
        Args:
            age: Edad a validar
            
        Returns:
            bool: True si la edad es válida
            
        Raises:
            InvalidAgeException: Si la edad es menor a 18 años
        """
        if age < 18:
            logger.warning(f"Edad inválida proporcionada: {age}")
            raise InvalidAgeException("La edad debe ser mayor o igual a 18 años")
        return True

    def validate_user_name(self, name: str) -> bool:
        """
        Valida que el nombre del usuario no esté vacío ni solo contenga espacios.
        
        Args:
            name: Nombre a validar
            
        Returns:
            bool: True si el nombre es válido
            
        Raises:
            InvalidUserNameException: Si el nombre está vacío o solo contiene espacios
        """
        if not name or not name.strip():
            logger.warning("Nombre de usuario inválido proporcionado")
            raise InvalidUserNameException("El nombre no puede estar vacío o solo contener espacios")
        return True

    def email_exists(self, email: str) -> bool:
        """
        Verifica si un email ya existe en el sistema.
        
        Args:
            email: Email a verificar
            
        Returns:
            bool: True si el email existe, False en caso contrario
        """
        try:
            logger.info(f"Verificando existencia de email: {email}")
            exists = self.user_repository.email_exists(email)
            logger.info(f"Email {email} existe: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error al verificar email: {str(e)}")
            raise AppBaseException(f"Error al verificar email: {str(e)}")

    def update_user_status(self, user_id: int, new_status: UserStatus) -> User:
        """
        Actualiza el estado de un usuario.
        
        Args:
            user_id: ID del usuario
            new_status: Nuevo estado del usuario
            
        Returns:
            User: Usuario actualizado
            
        Raises:
            UserNotFoundException: Si el usuario no existe
        """
        try:
            logger.info(f"Actualizando estado del usuario {user_id} a {new_status.value}")
            
            # Obtener usuario existente
            user = self.get_user_by_id(user_id)
            
            # Actualizar estado
            user.status = new_status
            
            # Guardar cambios (en un escenario real, necesitarías un método update en el repositorio)
            # Por ahora, esto es conceptual ya que el repositorio solo tiene save
            logger.info(f"Estado del usuario {user_id} actualizado exitosamente")
            return user
            
        except UserNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error al actualizar estado del usuario: {str(e)}")
            raise AppBaseException(f"Error al actualizar usuario: {str(e)}")

    def get_user_info(self, user_id: int) -> dict:
        """
        Obtiene información completa del usuario en formato dict.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            dict: Información del usuario
            
        Raises:
            UserNotFoundException: Si el usuario no existe
        """
        try:
            logger.info(f"Obteniendo información del usuario {user_id}")
            user = self.get_user_by_id(user_id)
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "age": user.age,
                "status": user.status.value
            }
        except UserNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error al obtener información del usuario: {str(e)}")
            raise AppBaseException(f"Error al obtener información del usuario: {str(e)}")
