class UserNotFound(Exception):
    """Пользователь не найден"""
    message = "User not found"
    code = "USER_NOT_FOUND"

class UserAlreadyBanned(Exception):
    message = "User already banned"
    code = "USER_ALREADY_BANNED"
    
class BanPrivilegeError(Exception):
    message = "The user does not have the necessary privileges"
    code = "BAN_USER_LOW_PRIVILEGE"