from sqlalchemy import Column, Integer, String

from src.models import BaseModel


class ExamCats(BaseModel):
    __tablename__ = "exam_categories"
    id: int = Column(Integer, primary_key=True, index=True)
<<<<<<< HEAD
    code: str = Column(String, nullable=False, unique=True)
    name: str = Column(String, nullable=False, unique=True)
    exam_group_id: int = Column(String, nullable=False, unique=False)
=======
    code: str = Column(String, nullable=False, unique=False)
    name: str = Column(String, nullable=False, unique=False)
    exam_group_id: int = Column(String, nullable=False, unique=False)
>>>>>>> 557b430fa6b9f6b214ff3d7a16a019592e1e6d59
