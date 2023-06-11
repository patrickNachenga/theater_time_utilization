from contextlib import contextmanager

import databases
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

metadata = sqlalchemy.MetaData()
database = databases.Database(settings.DATABASE_URL)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
uaa_engine = create_engine(settings.UAA_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, expire_on_commit=False, autoflush=False, bind=engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
