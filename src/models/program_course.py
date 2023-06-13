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

    # ______________________________________Relationships ____________________________________________#
    course = relationship('Course', lazy='subquery', back_populates="program_courses")
    course_category = relationship('CourseCategory', lazy='subquery', back_populates="program_courses")

    program_semester = relationship('ProgramSemester', lazy='subquery', back_populates="program_courses")

    program_course_assessments = relationship('ProgramCourseAssessment', lazy='subquery',
                                              back_populates="program_course")
    course_allocations = relationship("CourseAllocation", lazy="subquery", back_populates="program_course")

    student_course_registrations = relationship("StudentCourseRegistration", lazy="subquery",
                                                back_populates="program_course")

    student_exam_registration_program_course = relationship("StudentExamRegistration", lazy="subquery",
                                                            back_populates="program_course_student_exam_registration")

    exam_result_summary_program_course = relationship("ExamResultSummary", lazy="subquery",
                                                      back_populates="program_course_exam_result_summary")

    exam_result_program_course = relationship("ExamResult", lazy="subquery",
                                              back_populates="program_course_exam_result")

    exam_coursework_program_course = relationship("ExamCoursework", lazy="subquery",
                                                  back_populates="program_course_exam_coursework")
