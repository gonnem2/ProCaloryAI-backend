# src/api/graphql/schema.py
import logging
from typing import List, Any

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.types import ExecutionContext

from src.api.graphql.context import get_graphql_context
from src.api.graphql.mutations.auth import AuthMutation
from src.api.graphql.queries.user import UserQuery

logger = logging.getLogger(__name__)


def process_errors(errors: List[Any], execution_context: ExecutionContext) -> None:
    for error in errors:
        # GraphQLError от нас — ожидаемые, просто логируем как info
        if not hasattr(error, "original_error") or error.original_error is None:
            logger.info("GraphQL error: %s", error.message)
        else:
            # неожиданное исключение — логируем как критическое
            logger.exception(
                "Unexpected error in resolver: %s",
                error.message,
                exc_info=error.original_error,
            )


schema = strawberry.Schema(
    query=UserQuery,
    mutation=AuthMutation,
    process_errors=process_errors,  # ← глобальный обработчик
)

graphql_router = GraphQLRouter(
    schema,
    context_getter=get_graphql_context,
)
