import json

import requests

from src.core.config import settings
from src.db.session import session_scope
from src.helpers.utils import get_current_semester
from src.models import ProgramCourse, ProgramSemester, AcademicYear, CourseAllocation, Program, AcademicYearSemester, \
    StudentExamRegistration, ExamCategory
from src.models.student_course_registration import StudentCourseRegistration
from src.types import CourseRegistrationListNode, StudentUaaData, ProgramCourseListNode, StudentProgramCourseListNode, \
    ExamRegistrationListNode


class StudentService:
    """
    Retrieve all course registrations for a given student in the current year of study
    """

    def get_student_current_course_registration(self, student_uid) -> CourseRegistrationListNode:
        with session_scope() as session:
            semester = get_current_semester()

            result = session.query(StudentCourseRegistration). \
                join(ProgramCourse). \
                join(ProgramSemester). \
                join(AcademicYear). \
                filter(StudentCourseRegistration.student_uid == student_uid). \
                filter(AcademicYear.status == 1). \
                filter(ProgramSemester.semester == semester). \
                all()

            return CourseRegistrationListNode(items=result, total_count=len(result))

    def register_student_course(self, inputs) -> CourseRegistrationListNode:
        """
        Register Student course
        :param inputs:
        :return:
        """

        with session_scope() as session:
            final_student_uid = None
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
                        final_student_uid = data.student_uid
                        session.add(course_registration)
            session.commit()
            # getting current semester

            semester = get_current_semester()

            # getting student current semester course registration
            result = session.query(StudentCourseRegistration) \
                .join(ProgramCourse) \
                .join(ProgramSemester) \
                .filter(ProgramSemester.semester == semester) \
                .filter(StudentCourseRegistration.student_uid == final_student_uid,
                        StudentCourseRegistration.deleted_at.is_(None)).order_by(
                StudentCourseRegistration.id.desc()).all()

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
            # print('student_uids',student_uids)
            student_uids = [uid for uid, in student_uids]
            data = None
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

                response = requests.post(settings.UAA_URi + '/students-details-by-uids', data=data_json,
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
                join(AcademicYear). \
                filter(AcademicYear.status == 1). \
                filter(Program.uid == inputs.program_uid). \
                filter(ProgramSemester.semester == inputs.semester). \
                filter(ProgramSemester.study_year == inputs.study_year).all()
            total_count = len(program_courses)
            registered_course = session.query(StudentCourseRegistration). \
                join(ProgramCourse).join(ProgramSemester).join(AcademicYear).filter(AcademicYear.status == 1). \
                filter(StudentCourseRegistration.student_uid == inputs.student_uid). \
                filter(ProgramSemester.semester == inputs.semester).all()

            return StudentProgramCourseListNode(course_to_register=program_courses, total_count=total_count,
                                                course_registered=registered_course)
        pass

    def register_student_exam(self, inputs) -> ExamRegistrationListNode:
        """
        Register student exam
        :param inputs: exam_category and student_course_registration
        :return:ExamRegistrationListNode
        """

        with session_scope() as session:
            for data in inputs:

                course_registration = session.query(StudentCourseRegistration).filter(
                    StudentCourseRegistration.uid == data.course_registration_uid,
                    StudentCourseRegistration.deleted_at.is_(None)).first()
                exam_category = session.query(ExamCategory).filter(ExamCategory.uid == data.exam_category_uid,
                                                                   ExamCategory.deleted_at.is_(None)).first()
                if course_registration and exam_category:
                    exam_registration = session.query(StudentExamRegistration).filter(
                        StudentExamRegistration.student_course_registration == course_registration,
                        StudentExamRegistration.exam_category == exam_category,
                        StudentExamRegistration.deleted_at.is_(None)).first()
                    # Check if exam already exist, so that not to register once again

                    if exam_registration is None:
                        exam_registration = StudentExamRegistration(
                            exam_category=exam_category,
                            student_course_registrations=course_registration
                        )

                        session.add(exam_registration)
            session.commit()

            semester = get_current_semester()
            result = session.query(StudentExamRegistration).join(StudentCourseRegistration) \
                .join(ProgramCourse) \
                .join(ProgramSemester) \
                .filter(ProgramSemester.semester == semester) \
                .filter(
                StudentExamRegistration.deleted_at.is_(None)).order_by(StudentExamRegistration.id.desc()).all()

            return ExamRegistrationListNode(items=result, total_count=len(result))

    def get_student_current_exam_registration(self, student_uid) -> StudentExamRegistration:
        with session_scope() as session:
            semester = get_current_semester()
            result = session.query(StudentExamRegistration).join(StudentCourseRegistration) \
                .join(ProgramCourse) \
                .join(ProgramSemester) \
                .filter(StudentCourseRegistration.student_uid == student_uid) \
                .filter(ProgramSemester.semester == semester) \
                .filter(
                StudentExamRegistration.deleted_at.is_(None)).order_by(StudentExamRegistration.id.desc()).all()
            return result

