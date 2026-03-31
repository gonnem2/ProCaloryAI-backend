"""
Исключения сущности юезра
"""


class DomainException(Exception):
    """Базовое доменное исключение"""


class UserAlreadyExists(DomainException):
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists")


class InvalidCredentials(DomainException):
    def __init__(self):
        super().__init__("Invalid email or password")


class UserNotFound(DomainException):
    def __init__(self, identifier: str):
        super().__init__(f"User '{identifier}' not found")
