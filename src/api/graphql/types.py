# src/api/graphql/types.py
import strawberry


@strawberry.type
class UserGQL:
    id: int
    username: str
    email: str
    role: str


@strawberry.type
class AuthPayload:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@strawberry.input
class RegisterInput:
    username: str
    email: str
    password: str


@strawberry.input
class LoginInput:
    email: str
    password: str
