import logging

import strawberry
from strawberry.fastapi import GraphQLRouter

from src.api.graphql.context import get_graphql_context
from src.api.graphql.mutations.auth import AuthMutation
from src.api.graphql.queries.user import UserQuery

logger = logging.getLogger(__name__)


from strawberry.extensions import Extension


class ErrorLoggingExtension(Extension):
    def on_request_end(self):
        if self.execution_context.errors:
            for error in self.execution_context.errors:
                if error.original_error:
                    logger.exception(
                        "Unexpected error: %s",
                        error.message,
                        exc_info=error.original_error,
                    )
                else:
                    logger.info("GraphQL error: %s", error.message)


schema = strawberry.Schema(
    query=UserQuery,
    mutation=AuthMutation,
    extensions=[ErrorLoggingExtension],
)

graphql_router = GraphQLRouter(
    schema,
    context_getter=get_graphql_context,
)
