from fastapi import FastAPI
import uvicorn

from src.api.router import router
from src.infrastructure.database import orm

app = FastAPI()

app.include_router(router)


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
