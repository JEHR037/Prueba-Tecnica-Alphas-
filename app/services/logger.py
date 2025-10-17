import logging
import sys
from pathlib import Path


def setup_logger(
    name: str = "uvicorn.access",
    level: int = logging.DEBUG,
    log_file: str = "app.log",
    log_format: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
) -> logging.Logger:
    """
    Configura y retorna un logger con handlers para archivo y consola.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Nombre del archivo de log
        log_format: Formato de los mensajes de log
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicación de handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Formatter
    formatter = logging.Formatter(log_format)
    
    # File Handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Stream Handler (consola)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    
    # Agregar handlers
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger por nombre. Si no existe, lo crea con configuración por defecto.
    
    Args:
        name: Nombre del logger (usualmente __name__ del módulo)
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Si el logger no tiene handlers, configurarlo
    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        
        # Stream Handler
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    
    return logger


class LoggerManager:
    """
    Gestor centralizado de loggers para la aplicación.
    Singleton para mantener consistencia en toda la app.
    """
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance
    
    def get_logger(
        self,
        name: str,
        level: int = logging.DEBUG,
        log_file: str = "app.log"
    ) -> logging.Logger:
        """
        Obtiene o crea un logger con configuración específica.
        
        Args:
            name: Nombre del logger
            level: Nivel de logging
            log_file: Archivo de log
            
        Returns:
            logging.Logger: Logger configurado
        """
        if name not in self._loggers:
            self._loggers[name] = setup_logger(
                name=name,
                level=level,
                log_file=log_file
            )
        return self._loggers[name]
    
    def configure_all_loggers(self, level: int):
        """
        Cambia el nivel de logging para todos los loggers existentes.
        
        Args:
            level: Nuevo nivel de logging
        """
        for logger in self._loggers.values():
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)


# Instancia global del gestor de loggers
logger_manager = LoggerManager()


# Logger principal de la aplicación
app_logger = setup_logger(
    name="uvicorn.access",
    level=logging.DEBUG,
    log_file="app.log"
)


def log_function_call(func):
    """
    Decorador para loguear llamadas a funciones.
    
    Usage:
        @log_function_call
        def my_function(arg1, arg2):
            pass
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Llamando a {func.__name__} con args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completado exitosamente")
            return result
        except Exception as e:
            logger.error(f"Error en {func.__name__}: {str(e)}")
            raise
    return wrapper


def log_exception(logger: logging.Logger, exception: Exception, context: str = ""):
    """
    Loguea una excepción con contexto adicional.
    
    Args:
        logger: Logger a utilizar
        exception: Excepción a loguear
        context: Contexto adicional sobre dónde ocurrió el error
    """
    error_msg = f"Excepción capturada"
    if context:
        error_msg += f" en {context}"
    error_msg += f": {type(exception).__name__} - {str(exception)}"
    logger.error(error_msg, exc_info=True)


def log_request_response(logger: logging.Logger, method: str, url: str, status_code: int, duration_ms: float):
    """
    Loguea información de request/response HTTP.
    
    Args:
        logger: Logger a utilizar
        method: Método HTTP (GET, POST, etc.)
        url: URL del request
        status_code: Código de estado de la respuesta
        duration_ms: Duración del request en milisegundos
    """
    logger.info(
        f"{method} {url} - Status: {status_code} - Duration: {duration_ms:.2f}ms"
    )

