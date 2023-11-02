from contextlib import contextmanager

import databases
import sqlalchemy
from sqlalchemy import create_engine, event, func, Column, DateTime
from sqlalchemy.orm import sessionmaker, declared_attr, Query, Session

from src.core.config import settings

metadata = sqlalchemy.MetaData()
database = databases.Database(settings.DATABASE_URL)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_size=15, max_overflow=0)


class SoftDelete:
    @declared_attr
    def deleted_at(cls):
        return Column(DateTime, nullable=True)


class NotDeletedQuery(Query):
    _with_deleted = False

    def with_deleted(self):
        self._with_deleted = True
        return self

    def get(self, ident):
        print("get", ident)
        return super().get(ident) if self._with_deleted \
            else super().filter_by(deleted_at=None).get(ident)

    def __iter__(self):
        return super().__iter__() if self._with_deleted \
            else super().filter_by(deleted_at=None).__iter__()


class CustomSession(Session):
    def __init__(self, **options):
        super(CustomSession, self).__init__(**options)

    def query(self, *entities, **kwargs):
        return super(CustomSession, self).query(*entities, **kwargs).filter_by(deleted_at=None)

    _query_cls = NotDeletedQuery


SessionLocal = sessionmaker(autocommit=False, expire_on_commit=False, autoflush=False, bind=engine,
                            class_=CustomSession)


class CustomSessionDeleted(Session):
    def __init__(self, **options):
        super(CustomSessionDeleted, self).__init__(**options)

    def query(self, *entities, **kwargs):
        return super(CustomSessionDeleted, self).query(*entities, **kwargs)


SessionLocalDeleted = sessionmaker(autocommit=False, expire_on_commit=False, autoflush=False, bind=engine,
                                   class_=CustomSessionDeleted)


@contextmanager
def session_scope(withDeleted: bool = False):
    """Provide a transactional scope around a series of operations."""
    if withDeleted:
        session = SessionLocalDeleted()
    else:
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
