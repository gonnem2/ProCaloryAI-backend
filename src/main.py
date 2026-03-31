from fastapi import FastAPI
import uvicorn

from src.api.graphql.schema import graphql_router
from src.infrastructure.database import orm

app = FastAPI()

app.include_router(graphql_router, prefix="/graphql")


def main() -> None:
    orm.start_mappers()
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        reload=True,
        workers=1,
    )


if __name__ == "__main__":
    main()
