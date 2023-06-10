from src.db.session import session_scope
from src.models import ProgramCourse, ProgramSemester, AcademicYear
from src.models.student_course_registration import StudentCourseRegistration
from src.types import CourseRegistrationListNode


class StudentService:
    """
    Retrieve all course registrations for a given student in the current year of study
    """

    def get_student_current_course_registration(self, student_uid) -> CourseRegistrationListNode:
        with session_scope() as session:
            result = session.query(StudentCourseRegistration) \
                .join(ProgramCourse) \
                .join(ProgramSemester) \
                .join(AcademicYear) \
                .filter(StudentCourseRegistration.student_uid == student_uid) \
                .filter(StudentCourseRegistration.deleted_at.is_(None)) \
                .filter(AcademicYear.status.is_(1)) \
                .all()
            return CourseRegistrationListNode(items=result, total_count=len(result))

    def register_student_course(self, inputs) -> CourseRegistrationListNode:
        """
        Register Student course
        :param inputs:
        :return:
        """

        with session_scope() as session:
            for data in inputs:
                program_course = session.query(ProgramCourse).filter(ProgramCourse.uid == data.program_course_uid,
                                                                     ProgramCourse.deleted_at.is_(None)).first()
                # Check if program course already exist
                if program_course is None:
                    return CourseRegistrationListNode(items=[], total_count=0)
                course_registration = StudentCourseRegistration(
                    student_uid=data.student_uid,
                    core_elective=data.core_elective,
                    program_course=program_course
                )
                session.add(course_registration)
            session.commit()
            result = session.query(StudentCourseRegistration).filter(
                StudentCourseRegistration.deleted_at.is_(None)).order_by(StudentCourseRegistration.id.desc()).all()
            return CourseRegistrationListNode(items=result, total_count=len(result))
