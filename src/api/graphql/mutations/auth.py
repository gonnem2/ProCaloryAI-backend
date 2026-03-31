# src/api/graphql/mutations/auth.py
import strawberry
from strawberry.types import Info

from src.api.graphql.types import AuthPayload, RegisterInput, LoginInput, RefreshInput
from src.api.graphql.utils import handle_domain_errors
from src.application.service.user import UserService


def _service(info: Info) -> UserService:
    return UserService(info.context["uow"])


@strawberry.type
class AuthMutation:
    @strawberry.mutation()
    async def register(self, info: Info, input: RegisterInput) -> AuthPayload:
        async with handle_domain_errors():
            access, refresh = await _service(info).create_user(
                username=input.username,
                email=input.email,
                password=input.password,
            )
        return AuthPayload(access_token=access, refresh_token=refresh)

    @strawberry.mutation()
    async def login(self, info: Info, input: LoginInput) -> AuthPayload:
        async with handle_domain_errors():
            access, refresh = await _service(info).login(
                email=input.email,
                raw_password=input.password,
            )
        return AuthPayload(access_token=access, refresh_token=refresh)

    @strawberry.mutation()
    async def refresh_tokens(self, info: Info, input: RefreshInput) -> AuthPayload:
        async with handle_domain_errors():
            access, refresh = await _service(info).refresh(input.refresh_token)
        return AuthPayload(access_token=access, refresh_token=refresh)
