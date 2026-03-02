from fastapi import FastAPI
import uvicorn

from src.api.router import router
from src.infrastructure.database import orm

orm.start_mappers()
app = FastAPI()

app.include_router(router)


def main() -> None:
    uvicorn.run(
        "src.main:app",
        reload=True,
        workers=1,
    )


if __name__ == "__main__":
    main()
