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


# Define the attach_coursework_listener function
def attach_coursework_listener(additional_param1, additional_param2):
    def coursework_after_insert_or_update(mapper, connection, target, additional_param1=additional_param1,
                                          additional_param2=additional_param2):
        print('target: ', target, 'other params:', additional_param1, additional_param2)

    event.listen(ExamCoursework, 'after_insert', coursework_after_insert_or_update)
    event.listen(ExamCoursework, 'after_update', coursework_after_insert_or_update)
