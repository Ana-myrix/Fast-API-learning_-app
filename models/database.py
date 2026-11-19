import os
from collections.abc import Iterator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Reads the .env file in the project folder (if it exists) into environment variables.
load_dotenv()

# Set in .env, for example:
#   DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/fastapi_api
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Add it to the .env file in the project folder."
    )

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Give each request its own database session, and close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
