from pydantic import BaseModel, EmailStr


class UserIn(BaseModel):
    """Схема создания пользователя"""

    username: str
    email: EmailStr
    password: str
