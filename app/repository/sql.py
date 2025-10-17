from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, func
from typing import Optional

from app.models.domain import User, UserStatus
from app.models.base import UserRepository
from app.models.exception import (
    UserNotFoundException, 
    DuplicateEmailException, 
    InvalidAgeException, 
    InvalidUserNameException
)
from app.services.logger import get_logger, log_exception

logger = get_logger(__name__)


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self):
        """Inicializa el repositorio con SQLAlchemy en memoria."""
        logger.info("Inicializando SQLAlchemyUserRepository")
        
        # Motor en memoria - SOLO SIMULACIÓN
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        self.metadata = MetaData()
        
        # Definir tabla usuarios
        self.users = Table('users', self.metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('email', String(100), unique=True, nullable=False),
            Column('name', String(50), nullable=False),
            Column('status', String(20), nullable=False),
            Column('age', Integer, nullable=False)
        )
        
        # Crear tablas
        self.metadata.create_all(self.engine)
        self.connection = self.engine.connect()
        
        logger.info("SQLAlchemyUserRepository inicializado correctamente")

    def save(self, user: User) -> User:
        """Guarda un nuevo usuario en la base de datos."""
        try:
            logger.debug(f"Intentando guardar usuario con email: {user.email}")
            
            # Validar edad
            if user.age < 18:
                logger.warning(f"Edad inválida: {user.age}")
                raise InvalidAgeException("La edad debe ser mayor o igual a 18 años")

            # Validar nombre no nulo ni vacío o sólo espacios
            if not user.name or not user.name.strip():
                logger.warning("Nombre de usuario inválido")
                raise InvalidUserNameException("El nombre no puede estar vacío o en blanco")
            
            # Validar email duplicado
            if self.email_exists(user.email):
                logger.warning(f"Email duplicado: {user.email}")
                raise DuplicateEmailException("El email ya existe en la base de datos")

            # Preparar datos para INSERT
            values = {
                'email': user.email,
                'name': user.name,
                'status': user.status.value,
                'age': user.age
            }

            # Ejecutar INSERT
            result = self.connection.execute(self.users.insert(), values)
            self.connection.commit()
            
            # Asignar ID autoincremental
            user.id = result.inserted_primary_key[0] if result.inserted_primary_key else None
            
            logger.info(f"Usuario guardado exitosamente con ID: {user.id}")
            return user
            
        except (InvalidAgeException, InvalidUserNameException, DuplicateEmailException):
            raise
        except Exception as e:
            logger.error(f"Error inesperado al guardar usuario: {str(e)}")
            log_exception(logger, e, "save")
            raise UserNotFoundException(f"Error al guardar usuario: {str(e)}")

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca un usuario por su ID."""
        try:
            logger.debug(f"Buscando usuario con ID: {user_id}")
            
            # Ejecutar SELECT
            stmt = self.users.select().where(self.users.c.id == user_id)
            result = self.connection.execute(stmt)
            user_data = result.fetchone()
            
            # Si existe, convertir a User object
            if user_data:
                user = User(
                    id=user_data[0],
                    email=user_data[1],
                    name=user_data[2],
                    status=UserStatus(user_data[3]),
                    age=user_data[4]
                )
                logger.debug(f"Usuario encontrado: {user.email}")
                return user
            
            # Si no existe, lanzar excepción
            logger.warning(f"Usuario con ID {user_id} no encontrado")
            raise UserNotFoundException(f"Usuario con ID '{user_id}' no encontrado")
            
        except UserNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error al buscar usuario por ID: {str(e)}")
            log_exception(logger, e, "find_by_id")
            raise UserNotFoundException(f"Error al buscar usuario: {str(e)}")

    def email_exists(self, email: str) -> bool:
        """Verifica si un email ya existe en la base de datos."""
        try:
            logger.debug(f"Verificando existencia de email: {email}")
            
            # Ejecutar SELECT COUNT(*)
            stmt = self.users.select().with_only_columns(func.count()).where(self.users.c.email == email)
            result = self.connection.execute(stmt)
            count = result.scalar()
            
            exists = count > 0
            logger.debug(f"Email {email} existe: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Error al verificar email: {str(e)}")
            log_exception(logger, e, "email_exists")
            raise UserNotFoundException(f"Error al verificar email: {str(e)}")

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Busca un usuario por su email y retorna un diccionario."""
        try:
            logger.debug(f"Buscando usuario con email: {email}")
            
            result = self.connection.execute(self.users.select().where(self.users.c.email == email))
            user_data = result.fetchone()
            
            if user_data:
                user = User(
                    id=user_data[0],
                    email=user_data[1],
                    name=user_data[2],
                    status=UserStatus(user_data[3]),
                    age=user_data[4]
                )
                logger.debug(f"Usuario encontrado: {user.email}")
                return user.dict()
            else:
                logger.warning(f"Usuario con email {email} no encontrado")
                raise UserNotFoundException(f"Usuario con email '{email}' no existe")
                
        except (UserNotFoundException, DuplicateEmailException, InvalidAgeException, InvalidUserNameException) as e:
            logger.error(f"Error de validación: {str(e)}")
            return {'error': str(e)}
        except Exception as e:
            logger.error(f"Error inesperado al buscar usuario por email: {str(e)}")
            log_exception(logger, e, "get_user_by_email")
            return {'error': f"Error inesperado: {str(e)}"}
