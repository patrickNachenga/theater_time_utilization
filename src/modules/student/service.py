import json

import requests

from src.core.config import settings
from src.db.session import session_scope
from src.models import ProgramCourse, ProgramSemester, AcademicYear, CourseAllocation, Program, AcademicYearSemester
from src.models.student_course_registration import StudentCourseRegistration
from src.types import CourseRegistrationListNode, StudentUaaData, ProgramCourseListNode, StudentProgramCourseListNode


class StudentService:
    """
    Retrieve all course registrations for a given student in the current year of study
    """

    def get_student_current_course_registration(self, student_uid) -> CourseRegistrationListNode:
        with session_scope() as session:
            result = session.query(StudentCourseRegistration). \
                join(ProgramCourse). \
                join(ProgramSemester). \
                join(AcademicYear). \
                filter(StudentCourseRegistration.student_uid == student_uid). \
                filter(AcademicYear.status == 1). \
                all()

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

                if program_course:
                    course_registration = session.query(StudentCourseRegistration).filter(
                        StudentCourseRegistration.program_course == program_course,
                        StudentCourseRegistration.student_uid == data.student_uid,
                        StudentCourseRegistration.deleted_at.is_(None)).first()
                    # Check if registered course already exist, so that not to register once again

                    if course_registration is None:
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

    def get_allocation_students(self, allocation_uid) -> [StudentUaaData]:
        """
        Retrieve all students located to a particular allocation
        """
        with session_scope() as session:
            student_uids = session.query(StudentCourseRegistration.student_uid). \
                join(ProgramCourse). \
                join(CourseAllocation). \
                filter(CourseAllocation.uid == allocation_uid, CourseAllocation.deleted_at.is_(None)). \
                all()

            # Extract the student UIDs from the query result
            student_uids = [uid for uid, in student_uids]

            data_obj = {
                "uids": student_uids
            }
            try:
                # Serialize the data to JSON
                data_json = json.dumps(data_obj)

                # Set the Content-Type header to indicate that the request body is JSON
                headers = {
                    "Content-Type": "application/json"
                }

                response = requests.post(settings.UAA_URi+'/students-details-by-uids', data=data_json,
                                         headers=headers)
            except Exception as e:
                print(e)
                response = None
            if response.status_code == 200:
                data = response.json()

        return data

    def get_student_course_to_register(self, inputs) -> StudentProgramCourseListNode:
        with session_scope() as session:
            program_courses = session.query(ProgramCourse). \
                join(ProgramSemester). \
                join(Program). \
                join(AcademicYear).\
                filter(AcademicYear.status==1).\
                filter(Program.uid == inputs.program_uid). \
                filter(ProgramSemester.semester==inputs.semester).\
                filter(ProgramSemester.study_year == inputs.study_year).all()
            total_count = len(program_courses)
            registered_course = session.query(StudentCourseRegistration).\
                join(ProgramCourse).join(ProgramSemester).join(AcademicYear). filter(AcademicYear.status==1).\
                filter(StudentCourseRegistration.student_uid == inputs.student_uid). \
                filter(ProgramSemester.semester==inputs.semester).all()

            return StudentProgramCourseListNode(course_to_register=program_courses, total_count=total_count,course_registered=registered_course)
        pass
