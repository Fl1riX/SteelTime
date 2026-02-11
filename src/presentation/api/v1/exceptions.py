from fastapi import HTTPException, status
from src.logger import logger

class NoAccess(HTTPException):
    """Нет права доступа (403)"""
    def __init__(self, message: str = "Доступ запрещен"):
        logger.info(f"Ошибка 403: {message}")
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )

class NotFound(HTTPException):
    """Данные не найдены (404)"""
    def __init__(self, message: str = "Не найдено"):
        logger.info(f"Ошибка 404: {message}")
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )

class NotCorrect(HTTPException):
    """Не корректный запрос (400)"""
    def __init__(self, message: str = "Некорректный запрос"):
        logger.info(f"Ошибка 400: {message}")
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

class ConflictError(HTTPException):
    """Конфликт данных (409)"""
    def __init__(self, message: str = "Конфликт данных"):
        logger.info(f"Ошибка 409: {message}")
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )

class Unauthorized(HTTPException):
    """Требуется авторизация (401)"""
    def __init__(self, message: str = "Требуется авторазиция"):
        logger.info(f"Ошибка 401: {message}")
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )