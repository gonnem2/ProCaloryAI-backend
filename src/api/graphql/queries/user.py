import strawberry
from strawberry.types import Info

from src.api.graphql.types import UserGQL


@strawberry.type
class UserQuery:
    @strawberry.field()
    async def me(self, info: Info) -> UserGQL:
        user = info.context.get("current_user")
        if user is None:
            raise strawberry.exceptions.GraphQLError("Not authenticated")

        return UserGQL(**user)
