from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from models.database import SessionLocal
from routes import auth, general, items
from services import auth_service
from services.errors import AppError


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts. Tables must exist first
    # (run: alembic upgrade head).
    with SessionLocal() as db:
        auth_service.ensure_demo_user(db)
    yield


app = FastAPI(title="FastAPI API", lifespan=lifespan)


# Turns AppError from the services into a normal JSON error response.
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app.include_router(general.router)
app.include_router(auth.router)
app.include_router(items.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
