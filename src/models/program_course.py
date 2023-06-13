from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from src.models import BaseModel


class ProgramCourse(BaseModel):
    __tablename__ = "program_courses"
    credit: float = Column(Float(4), nullable=True)
    lecture_hours: float = Column(Float(4), nullable=True)
    seminar_hours: float = Column(Float(4), nullable=True)
    practical_hours: float = Column(Float(4), nullable=True)
    assignment_hours: float = Column(Float(4), nullable=True)
    independent_study_hours: float = Column(Float(4), nullable=True)
    pass_hours: float = Column(Float(4), nullable=True)
    moodle_id: str = Column(String, nullable=True)

    # ___________________________Foreign Keys ____________________________#
    course_category_id: int = Column(Integer, ForeignKey("course_categories.id"), nullable=False)

    program_semester_id: int = Column(Integer, ForeignKey("program_semesters.id"), nullable=False)

    course_id: int = Column(Integer, ForeignKey("courses.id"), nullable=False)

    # ____________________________Relationships ______________________#
    course = relationship('Course', lazy='subquery', back_populates="program_courses")
    course_category = relationship('CourseCategory', lazy='subquery', back_populates="program_courses")

    program_semester = relationship('ProgramSemester', lazy='subquery', back_populates="program_courses")

    program_course_assessments = relationship('ProgramCourseAssessment', lazy='subquery',
                                              back_populates="program_course")
    course_allocations = relationship("CourseAllocation", lazy="subquery", back_populates="program_course")

    student_course_registrations = relationship("StudentCourseRegistration", lazy="subquery",
                                                back_populates="program_course")
    exam_result_summary = relationship("ExamResultSummary", lazy="subquery", back_populates="program_course")

    program_course_exam_registration = relationship("StudentExamRegistration", lazy="subquery",
                                                    back_populates="student_exam_registrations")

    program_course_exam_result_summary = relationship("ProgramCourse", lazy="subquery",
                                                      back_populates="exam_result_summary_program_course")

    program_course_exam_result = relationship("ProgramCourse", lazy="subquery",
                                              back_populates="exam_result_program_course")

    program_course_exam_coursework = relationship("ProgramCourse", lazy="subquery",
                                                  back_populates="exam_coursework_program_course")
