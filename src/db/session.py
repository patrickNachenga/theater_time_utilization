from contextlib import contextmanager

import databases
import sqlalchemy
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.models import ExamCoursework, ExamResult

metadata = sqlalchemy.MetaData()
database = databases.Database(settings.DATABASE_URL)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

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


@event.listens_for(ExamCoursework, 'after_insert')
@event.listens_for(ExamCoursework, 'after_update')
def coursework_after_insert(mapper, connection, target):
    print('signal working',target,'type',type(target))


@event.listens_for(ExamResult, 'after_insert')
def result_after_insert(mapper, connection, target):
    print('signal working')
