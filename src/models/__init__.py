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


from .fee_structure import FeeStructure


from .control_number import ControlNumber

from .fee_structure import FeeStructure
from .program_category import ProgramCategory
from .course import Course
from .course_learn_outcome import CourseLearnOutcome
from .exam_category_group import ExamCategoryGroup
from .program import Program
from .group import Group
from .program_semester import ProgramSemester
from .course_category import CourseCategory
from .program_course import ProgramCourse
from .exam_category import ExamCategory
from .exam_result import ExamResults
from .exam_summary import ExamSummary
from .academic_year import AcademicYear
from .program_course_assessment import ProgramCourseAssessment
from .course_allocation import CourseAllocation
from .program_capacity import ProgramCapacity
from .semester_registration import SemesterRegistration
from .student_course_registration import StudentCourseRegistration
