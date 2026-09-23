from sqlalchemy import inspect, text
from sqlalchemy.orm import declarative_base
from sqlmodel import Session, create_engine

from app.core.config import get_settings

settings = get_settings()

# SQLite requires check_same_thread=False for FastAPI's threaded request handling.
_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=_connect_args, echo=False)
Base = declarative_base()


def get_db():
    """Provide one SQLModel/SQLAlchemy session per request."""
    with Session(engine) as session:
        yield session

    """Add identity columns needed by the domain model to an older local DB."""
    if not settings.database_url.startswith("sqlite"):
        return
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        return
    columns = {column["name"] for column in inspector.get_columns("users")}
    additions = {
        "email": "VARCHAR(320)",
        "full_name": "VARCHAR(200)",
        "is_active": "BOOLEAN NOT NULL DEFAULT 1",
    }
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN {name} {definition}"))