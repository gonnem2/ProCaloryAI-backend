from fastapi import Request, Depends
from typing import Annotated

from src.application.service.user import UserService
from src.infrastructure.uow import AbstractUnitOfWork, get_uow


async def get_graphql_context(
    request: Request,
    uow: Annotated[AbstractUnitOfWork, Depends(get_uow)],
) -> dict:
    token = _extract_bearer(request)
    current_user = None

    if token:
        # каждый запрос — свой UoW, не переиспользуем
        service = UserService(uow)
        current_user = await service.get_user_by_token(token)

    return {
        "uow": uow,
        "current_user": current_user,
    }


def _extract_bearer(request: Request) -> str | None:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header.removeprefix("Bearer ").strip()
    return None
