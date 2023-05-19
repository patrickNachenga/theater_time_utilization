from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Course(Base):
    __tablename__ = "course"
    id: int = Column(Integer, primary_key=True, index=True)
    description: str = Column(String, nullable=True, unique=True)
    name: str = Column(String, nullable=False, unique=False)
    code: str = Column(String, nullable=False, unique=False)
