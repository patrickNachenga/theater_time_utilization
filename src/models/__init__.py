import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=True)


from .staff import Staff
from .student import Student
from .program_category import ProgramCategory
from .course import Course
from .program import Program
from .group import Group
from .program_semester import ProgramSemester
from .program_course import ProgramCourse
from .exam_cat_groups import ExamCatGroups
from .exam_cats import ExamCats
from .exam_results import ExamResults
from .exam_summary import ExamSummary
from .academic_year import AcademicYear
from .course_assessment import CourseAssessment
