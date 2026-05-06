import logging
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.extensions import Extension

from src.api.graphql.context import get_graphql_context
from src.api.graphql.mutations.auth import AuthMutation
from src.api.graphql.mutations.nutrition import NutritionMutation
from src.api.graphql.queries.nutrition import AppQuery

logger = logging.getLogger(__name__)


@strawberry.type
class Mutation(NutritionMutation, AuthMutation):
    pass


class ErrorLoggingExtension(Extension):
    def on_request_end(self):
        for error in self.execution_context.errors or []:
            if error.original_error:
                logger.exception("Unexpected error", exc_info=error.original_error)
            else:
                logger.info("GraphQL error: %s", error.message)


schema = strawberry.Schema(
    query=AppQuery,
    mutation=Mutation,
    extensions=[ErrorLoggingExtension],
)

graphql_router = GraphQLRouter(schema, context_getter=get_graphql_context)
