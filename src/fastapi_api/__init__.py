import uvicorn
from fastapi import FastAPI

from .auth import router as auth_router

app = FastAPI(title="FastAPI API")
app.include_router(auth_router)


def main() -> None:
    uvicorn.run("fastapi_api:app", host="127.0.0.1", port=8000)
