from contextlib import asynccontextmanager

import strawberry

from src.domain.exceptions.base import DomainException


@asynccontextmanager
async def handle_domain_errors():
    """
    Оборачивает resolver — доменные ошибки превращает в GraphQLError,
    всё остальное пробрасывает дальше (поймает process_errors).
    """
    try:
        yield
    except DomainException as e:
        raise strawberry.exceptions.GraphQLError(str(e))
