class AppBaseException(Exception):
    """Clase base para excepciones personalizadas de la aplicación."""
    def __init__(self, message=None):
        base_message = "Alphas Error: "
        if message:
            self.message = f"{base_message}{message}"
        else:
            self.message = f"{base_message}Ocurrió un error en la aplicación"
        super().__init__(self.message)

class UserNotFoundException(AppBaseException):
    """Se lanza cuando un usuario no es encontrado."""
    def __init__(self, message="Usuario no encontrado"):
        alpha_message = f"Alphas Error: {message}"
        super().__init__(alpha_message)

class DuplicateEmailException(AppBaseException):
    """Se lanza cuando un email de usuario ya existe."""
    def __init__(self, message="El email ya existe en la base de datos"):
        alpha_message = f"Alphas Error: {message}"
        super().__init__(alpha_message)

class InvalidAgeException(AppBaseException):
    """Se lanza cuando la edad del usuario no es válida."""
    def __init__(self, message="La edad del usuario no es válida"):
        alpha_message = f"Alphas Error: {message}"
        super().__init__(alpha_message)

class InvalidUserNameException(AppBaseException):
    """Se lanza cuando el nombre de usuario es inválido."""
    def __init__(self, message="El nombre de usuario no puede estar vacío o solo contener espacios"):
        alpha_message = f"Alphas Error: {message}"
        super().__init__(alpha_message)


