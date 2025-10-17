"""
Módulo API - Contiene todas las rutas y endpoints de la aplicación.

Este módulo separa las rutas de la lógica principal de la aplicación,
siguiendo el principio de separación de responsabilidades.
"""

from app.api.routes import router, set_user_service

__all__ = ["router", "set_user_service"]
