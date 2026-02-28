from fastapi import FastAPI
import uvicorn

from src.api.router import router

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