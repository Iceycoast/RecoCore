from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL is not configured")

engine = create_engine(
    settings.DATABASE_URL,
    echo = False
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    
    finally: 
        db.close()