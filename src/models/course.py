from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Course(Base):
    __tablename__ = "course"
    id: int = Column(Integer, primary_key=True, index=True)
    description: str = Column(String, nullable=True, unique=False)
    name: str = Column(String, nullable=False, unique=False)
    short_name: str = Column(String, nullable=True, unique=False)
    code: str = Column(String, nullable=False, unique=False)
    offered: int = Column(Integer, nullable=False, unique=False)
    department_uid: int = Column(Integer, nullable=False, unique=False)

