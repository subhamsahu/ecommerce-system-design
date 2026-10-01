from sqlmodel import Session, create_engine
from sqlmodel import SQLModel

from app.core.config import get_settings

settings = get_settings()

# SQLite requires check_same_thread=False for FastAPI's threaded request handling.
_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(
    settings.database_url, 
    connect_args=_connect_args, 
    echo=False,
    pool_size=15,
    max_overflow=0,
    pool_timeout=30,
)
def get_db():
    """Provide one session per request and never perform schema changes here."""
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
