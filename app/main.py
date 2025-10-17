from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import time

from app.models.exception import (
    UserNotFoundException,
    DuplicateEmailException,
    InvalidAgeException,
    InvalidUserNameException,
    AppBaseException
)
from app.repository.sql import SQLAlchemyUserRepository
from app.services.userService import UserService
from app.services.logger import app_logger, log_request_response
from app.api.routes import router, set_user_service

# Logger configurado desde el módulo centralizado
logger = app_logger

# Inicializar FastAPI
app = FastAPI(
    title="Alphas User Management API",
    description="API para gestión de usuarios con patrón Repository",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Inicializar Repository y Service (Dependency Injection manual)
user_repository = SQLAlchemyUserRepository()
user_service = UserService(user_repository)

# Configurar el servicio en las rutas
set_user_service(user_service)

# Incluir las rutas de la API
app.include_router(router)


# ==================== Middleware ====================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de todas las peticiones HTTP."""
    logger.debug(f"Inbound request: {request.method} {request.url} (headers={dict(request.headers)})")
    start_time = time.time()
    logger.debug("Calling next(request) to proceed with request.")
    response = await call_next(request)
    logger.debug("Returned from next(request), preparing to send response.")
    process_time = (time.time() - start_time) * 1000
    
    # Usar función centralizada de logging
    log_request_response(
        logger=logger,
        method=request.method,
        url=str(request.url.path),
        status_code=response.status_code,
        duration_ms=process_time
    )
    
    return response


# ==================== Exception Handlers ====================

@app.exception_handler(UserNotFoundException)
async def user_not_found_exception_handler(request: Request, exc: UserNotFoundException):
    """Maneja excepciones de usuario no encontrado."""
    logger.error(f"UserNotFoundException: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Usuario no encontrado", "detail": exc.message}
    )


@app.exception_handler(DuplicateEmailException)
async def duplicate_email_exception_handler(request: Request, exc: DuplicateEmailException):
    """Maneja excepciones de email duplicado."""
    logger.error(f"DuplicateEmailException: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error": "Email duplicado", "detail": exc.message}
    )


@app.exception_handler(InvalidAgeException)
async def invalid_age_exception_handler(request: Request, exc: InvalidAgeException):
    """Maneja excepciones de edad inválida."""
    logger.error(f"InvalidAgeException: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Edad inválida", "detail": exc.message}
    )


@app.exception_handler(InvalidUserNameException)
async def invalid_username_exception_handler(request: Request, exc: InvalidUserNameException):
    """Maneja excepciones de nombre de usuario inválido."""
    logger.error(f"InvalidUserNameException: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Nombre de usuario inválido", "detail": exc.message}
    )


@app.exception_handler(AppBaseException)
async def app_base_exception_handler(request: Request, exc: AppBaseException):
    """Maneja excepciones genéricas de la aplicación."""
    logger.error(f"AppBaseException: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Error en la aplicación", "detail": exc.message}
    )


# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación."""
    logger.info("="*60)
    logger.info("Iniciando Alphas User Management API v1.0.0")
    logger.info("="*60)
    logger.info("Repository: SQLAlchemy (In-Memory)")
    logger.info("Logger: Configurado y activo")
    logger.info("Endpoints: Disponibles en /docs")
    logger.info("="*60)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación."""
    logger.info("="*60)
    logger.info("Cerrando Alphas User Management API")
    logger.info("="*60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="debug"
    )
