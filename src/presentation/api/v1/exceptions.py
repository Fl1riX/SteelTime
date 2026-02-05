from fastapi import HTTPException, status

class NoAccess(HTTPException):
    """Нет права доступа (403)"""
    def __init__(self, message: str = "Доступ запрещен"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )

class NotFound(HTTPException):
    """Данные не найдены (404)"""
    def __init__(self, message: str = "Не найдено"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )

class NotCorrect(HTTPException):
    """Не корректный запрос (400)"""
    def __init__(self, message: str = "Некорректный запрос"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

class ConflictError(HTTPException):
    """Конфликт данных (409)"""
    def __init__(self, message: str = "Конфликт данных"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )

class Unauthorized(HTTPException):
    """Требуется авторизация (401)"""
    def __init__(self, message: str = "Требуется авторазиция"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )