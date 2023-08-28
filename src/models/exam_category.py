from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ExamCategory(BaseModel):
    __tablename__ = "exam_categories"
    code: str = Column(String, nullable=False, unique=False)
    name: str = Column(String, nullable=False, unique=False)
    is_ue: bool = Column(Boolean, default=False)
    is_theory: bool = Column(Boolean, default=False)


    # _______________________________Foreign Keys___________________________________#

    # exam_category_group_id: int = Column(Integer, ForeignKey("exam_category_groups.id"), nullable=False)

    # _____________________________Relationships____________________________________#

    # exam_category_group = relationship('ExamCategoryGroup', lazy='subquery', back_populates="exam_categories")

    program_course_assessments = relationship('ProgramCourseAssessment', lazy='subquery',
                                              back_populates="exam_category")

    exam_results = relationship("ExamResult", lazy="subquery",
                                back_populates="exam_category")

    exam_courseworks = relationship("ExamCoursework", lazy="subquery",
                                    back_populates="exam_category")



    program_course_assessments = relationship('ProgramCourseAssessment', lazy='subquery',
                                              back_populates="exam_category")
