# src/api/graphql/mutations/auth.py
import strawberry
from strawberry.types import Info

from src.api.graphql.types import AuthPayload, RegisterInput, LoginInput, RefreshInput
from src.api.graphql.utils import handle_domain_errors, require_auth
from src.application.service.user import UserService


@strawberry.type
class AuthMutation:
    @strawberry.mutation
    async def register(self, info: Info, input: RegisterInput) -> AuthPayload:
        async with handle_domain_errors():
            access, refresh = await UserService(info.context["uow"]).create_user(
                username=input.username,
                email=input.email,
                password=input.password,
            )
        return AuthPayload(access_token=access, refresh_token=refresh)

    @strawberry.mutation
    async def login(self, info: Info, input: LoginInput) -> AuthPayload:
        async with handle_domain_errors():
            access, refresh = await UserService(info.context["uow"]).login(
                email=input.email,
                raw_password=input.password,
            )
        return AuthPayload(access_token=access, refresh_token=refresh)

    @strawberry.mutation
    async def refresh_tokens(self, info: Info, input: RefreshInput) -> AuthPayload:
        async with handle_domain_errors():
            access, refresh = await UserService(info.context["uow"]).refresh(
                input.refresh_token
            )
        return AuthPayload(access_token=access, refresh_token=refresh)

    @strawberry.mutation
    async def delete_account(self, info: Info) -> bool:
        user = require_auth(info)
        from src.application.service.profile import ProfileService

        async with handle_domain_errors():
            await ProfileService(info.context["uow"]).delete_account(user.id)
        return True
