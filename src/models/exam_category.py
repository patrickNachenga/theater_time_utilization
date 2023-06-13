from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ExamCategory(BaseModel):
    __tablename__ = "exam_categories"
    code: str = Column(String, nullable=False, unique=False)
    name: str = Column(String, nullable=False, unique=False)

    # _______________________________Foreign Keys___________________________________#

    exam_category_group_id: int = Column(Integer, ForeignKey("exam_category_groups.id"), nullable=False)


    # _____________________________Relationships____________________________________#

    exam_category_group = relationship('ExamCategoryGroup', lazy='subquery',
                                       back_populates="exam_categories")

    exam_category_exam_result_summary = relationship("ExamCategory", lazy="subquery",
                                                     back_populates="exam_result_summary_exam_category")

    exam_category_exam_result = relationship("ExamCategory", lazy="subquery",
                                             back_populates="exam_result_exam_category")

    exam_category_exam_coursework = relationship("ExamCategory", lazy="subquery",
                                                 back_populates="exam_coursework_exam_category")

    exam_category_student_exam_registration = relationship("ExamCategory", lazy="subquery",
                                                           back_populates="student_exam_registration_exam_category")

    program_course_assessments = relationship('ProgramCourseAssessment', lazy='subquery', back_populates="exam_category")



