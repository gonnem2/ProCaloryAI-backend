from typing import Annotated

from fastapi import APIRouter, Depends
from src.api.schemas import user
from src.application.service import user as user_service
from src.infrastructure.uow import AbstractUnitOfWork, get_uow

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/")
async def create_user(
    user: user.UserIn, uow: Annotated[AbstractUnitOfWork, Depends(get_uow)]
):
    service = user_service.UserService(uow)

    await service.create_user(
        username=user.username,
        email=str(user.email),
        password=user.password,
    )
