class UserNotFound(Exception):
    """Пользовател не найден"""
    message = "User not found"
    code = "USER_NOT_FOUND"