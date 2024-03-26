import json
from datetime import datetime
from typing import List

import requests
from sqlalchemy import and_
from sqlalchemy.orm import aliased
from src.shared.response import Response

from src.core.config import settings
from src.db.session import session_scope
from src.helpers.utils import get_current_semester, get_student_from_uaa, get_student_from_uaa_by_reg_numbers, \
    insert_exam_result, insert_course_work, \
    general_upload
from src.models import ProgramCourse, ProgramSemester, AcademicYear, CourseAllocation, Program, AcademicYearSemester, \
    StudentExamRegistration, ExamCategory, StudentExamFailure, StudentExamPostponement, ExamResult, ExamCoursework, \
    Course
from src.models.student_course_registration import StudentCourseRegistration
from src.shared.response_code import ResponseCode
from src.types import CourseRegistrationListNode, StudentUaaData, ProgramCourseListNode, StudentProgramCourseListNode, \
    ExamRegistrationListNode, ExamToRegister, UploadResponse, FailedStudent, ForceCoreCourseRegistrationInputNode, \
    ForceCoreCourseRegistrationOutput


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

    def force_core_course_registration(self, input: ForceCoreCourseRegistrationInputNode) -> List[
        ForceCoreCourseRegistrationOutput]:
        with session_scope() as session:
            academic_year = session.query(AcademicYear.id,
                                          AcademicYear.name).filter(AcademicYear.uid == input.academic_year_uid,
                                                                    AcademicYear.status == 1, AcademicYear.deleted_at.is_(None)).first()
            if academic_year is None:
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Selected academic year is not active",
                    data=ForceCoreCourseRegistrationOutput(program_code=None, program_name=None))

            if input.semester not in ['Odd', 'Even']:
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Invalid Semester Selection",
                    data=ForceCoreCourseRegistrationOutput(program_code=None, program_name=None))

            summary = []
            results = session.query(ProgramSemester.id, ProgramSemester.semester, ProgramSemester.program_id,
                                    Program.name.label('program_name'), Program.code.label('program_code')). \
                join(Program, Program.id == ProgramSemester.program_id). \
                filter(and_(
                ProgramSemester.academic_year.has(id=academic_year.id),
                ProgramSemester.deleted_at.is_(None),
                ProgramSemester.semester % 2 == (0 if input.semester == 'Even' else 1)
            )).order_by(ProgramSemester.program_id.asc()).all()

            if len(results) == 0:
                return Response(
                    status=True,
                    code=ResponseCode.FAILURE,
                    message="No any Program Semester is available",
                    data=False)

            for result in results:
                total_students = 0
                registered = 0
                pushed = 0
                not_registered = 0

                # Get Core Program Courses For this program semester
                core_course = session.query(ProgramCourse.id). \
                    filter(ProgramCourse.program_semester_id == result.id,
                           ProgramCourse.deleted_at.is_(None), ProgramCourse.course_category_id == 1).all()
                # print(f"{result.program_code} ==> Semester : {result.semester}")
                total_courses = len(core_course)
                if len(core_course) > 0:
                    # Check Students Registered For at least 1 subject for this program  semester
                    student_uids = session.query(StudentCourseRegistration.student_uid). \
                        join(ProgramCourse, ProgramCourse.id == StudentCourseRegistration.program_course_id).join(
                        ProgramSemester, ProgramSemester.id == ProgramCourse.program_semester_id). \
                        filter(
                        and_(
                            ProgramSemester.id == result.id,
                            ProgramSemester.deleted_at.is_(None),
                            ProgramCourse.deleted_at.is_(None),
                        )
                    ).group_by(StudentCourseRegistration.student_uid).all()
                    # total_students = len(student_uids)
                    total_students = len(student_uids)
                    if len(student_uids) > 0:
                        for student in student_uids:
                            for p_course in core_course:
                                # get list of courses the student is not registered
                                is_registered = session.query(StudentCourseRegistration.program_course_id). \
                                    filter(StudentCourseRegistration.program_course_id == p_course.id,
                                           StudentCourseRegistration.student_uid == student.student_uid,
                                           StudentCourseRegistration.deleted_at.is_(None)).first()
                                if is_registered:
                                    registered += 1
                                else:
                                    not_registered += 1
                                    course_registration = StudentCourseRegistration(
                                        student_uid=student.student_uid,
                                        core_elective=1,
                                        program_course_id=p_course.id
                                    )
                                    # session.add(course_registration)
                                    pushed += 1

                        #     print(f"====================> {course.id}")

                summary.append(ForceCoreCourseRegistrationOutput(
                    program_name=result.program_name,
                    program_code=result.program_code,
                    total_courses=total_courses,
                    course_entry_registered=registered,
                    course_entry_not_registered=not_registered,
                    course_entry_to_be_registered=total_students * total_courses,
                    course_entry_pushed=pushed,
                    total_students=total_students))

            session.commit()
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Course Registered successfully",
                data=summary)

    def register_student_course(self, inputs, uids_to_update) -> CourseRegistrationListNode:
        """
        Register Student course
        :param inputs, uids_to_update:
        :return:
        """

        with session_scope() as session:

            # Update deleted_at for the specified uids
            session.query(StudentCourseRegistration).filter(StudentCourseRegistration.uid.in_(uids_to_update)). \
                update({"deleted_at": datetime.now()})
            # insert new one
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

    def get_allocation_students(self, allocation_uid, assessment_number, exam_category, out_off, sort_excel) -> [
        StudentUaaData]:
        """
        Retrieve all students located to a particular allocation
        """

        print('reached: get_allocation_students()')
        with session_scope() as session:
            student_uids = session.query(StudentCourseRegistration.student_uid). \
                join(ProgramCourse). \
                join(CourseAllocation). \
                filter(CourseAllocation.uid == allocation_uid, CourseAllocation.deleted_at.is_(None)). \
                all()

            print('reached: get_allocation_students() : student_uids')
            # Extract the student UIDs from the query result
            allocation = session.query(CourseAllocation).filter(CourseAllocation.uid == allocation_uid,
                                                                CourseAllocation.deleted_at.is_(None)).first()
            print('reached: get_allocation_students() : allocation')

            program_course = None

            if allocation:
                # Assuming CourseAllocation has a foreign key to ProgramCourse
                program_course = allocation.program_course

            student_uids = [uid for uid, in student_uids]
            data = None
            data_obj = {
                "uids": student_uids,
                "excel_sort_type": sort_excel
            }
            try:
                # Serialize the data to JSON
                data_json = json.dumps(data_obj)

                # Set the Content-Type header to indicate that the request body is JSON
                headers = {
                    "Content-Type": "application/json"
                }

                response = requests.post(settings.UAA_URi + '/students-details-by-uids', data=data_json,
                                         headers=headers, timeout=5)

            except Exception as e:
                print(e)
                response = None
            if response.status_code == 200:
                response_data = response.json()
                data = {'data': response_data, "program_course": program_course}
                if session.query(ExamCategory).filter(ExamCategory.id == exam_category).first().is_ue:
                    ue_results = session.query(ExamResult).filter(
                        ExamResult.program_course_id == allocation.program_course.id,
                        ExamResult.exam_category_id == exam_category,
                        ExamResult.number_of_sitting == assessment_number).all()
                    ue_results_dict = {ue_result.student_uid: ue_result.score for ue_result in ue_results}
                    # Update the data list with marks from ue_results
                    for item in data['data']:
                        uid = item.get("uid")  # Use item.get to safely retrieve the UID
                        if uid is not None:
                            marks = ue_results_dict.get(uid, '')  # Retrieve the marks as a string
                            if marks:
                                item["marks"] = float(marks) * out_off / 100  # Convert the string to a float
                                if isinstance(item["marks"], (int, float)):
                                    item["marks"] = round(item["marks"], 1)
                            else:
                                item["marks"] = ''  # Set a default value if marks is empty

                        else:
                            item['marks'] = ''

                else:

                    course_work_results = session.query(ExamCoursework).filter(
                        ExamCoursework.program_course_id == allocation.program_course.id,
                        ExamCoursework.exam_category_id == exam_category,
                        ExamCoursework.assessment_number == assessment_number).all()

                    # for ue_course_work_result in course_work_results:
                    #
                    #     for item in data["data"]:
                    #         if ue_course_work_result.student_uid == item["uid"]:
                    #             item["marks"] = ue_course_work_result.score
                    #             print('marks',item["marks"])
                    ue_results_dict = {ue_result.student_uid: ue_result.score for ue_result in course_work_results}
                    # Update the data list with marks from ue_results
                    for item in data['data']:
                        # print(item)  # Print the entire item to inspect its structure
                        uid = item.get("uid")  # Use item.get to safely retrieve the UID
                        if uid is not None:
                            marks = ue_results_dict.get(uid, '')  # Retrieve the marks as a string
                            if marks:
                                item["marks"] = float(marks) * out_off / 100  # Convert the string to a float
                                if isinstance(item["marks"], (int, float)):
                                    item["marks"] = round(item["marks"], 1)
                            else:
                                item["marks"] = ''  # Set a default value if marks is empty

                        else:
                            item['marks'] = ''
        return data

    def get_student_course_to_register(self, inputs) -> StudentProgramCourseListNode:
        with (session_scope() as session):
            program_courses = session.query(ProgramCourse). \
                join(ProgramSemester). \
                join(Program). \
                join(AcademicYear). \
                filter(AcademicYear.status == 1). \
                filter(Program.uid == inputs.program_uid). \
                filter(ProgramSemester.semester == inputs.semester, ProgramSemester.deleted_at.is_(None)). \
                filter(ProgramSemester.study_year == inputs.study_year).all()

            total_count = len(program_courses)
            registered_course = session.query(StudentCourseRegistration). \
                join(ProgramCourse).join(ProgramSemester).join(AcademicYear).filter(AcademicYear.status == 1). \
                filter(StudentCourseRegistration.student_uid == inputs.student_uid,
                       StudentCourseRegistration.deleted_at.is_(None)). \
                filter(ProgramSemester.semester == inputs.semester).all()
            return StudentProgramCourseListNode(course_to_register=program_courses, total_count=total_count,
                                                course_registered=registered_course)
        pass

    def register_student_exam(self, inputs) -> ExamRegistrationListNode:
        """
        Register student exam
        :param inputs: exam type(1,2,3,4) and student_course_registration
        :return:ExamRegistrationListNode
        """
        student_uid = None
        with session_scope() as session:
            for data in inputs:

                course_registration = session.query(StudentCourseRegistration).filter(
                    StudentCourseRegistration.uid == data.course_registration_uid,
                    StudentCourseRegistration.deleted_at.is_(None)).first()

                if course_registration:
                    student_uid == course_registration.student_uid
                    exam_registration = session.query(StudentExamRegistration).filter(
                        StudentExamRegistration.student_course_registration == course_registration,
                        StudentExamRegistration.type == data.type,
                        StudentExamRegistration.deleted_at.is_(None)).first()
                    # Check if exam already exist, so that not to register once again
                    if exam_registration is None:
                        exam_registration = StudentExamRegistration(
                            type=data.type,
                            student_course_registration=course_registration
                        )

                        session.add(exam_registration)
            session.commit()

            semester = get_current_semester()
            result = session.query(StudentExamRegistration).join(StudentCourseRegistration) \
                .join(ProgramCourse) \
                .join(ProgramSemester) \
                .filter(StudentCourseRegistration.student_uid == course_registration.student_uid) \
                .filter(ProgramSemester.semester == semester) \
                .filter(
                StudentExamRegistration.deleted_at.is_(None)).order_by(StudentExamRegistration.id.desc()).all()

            return ExamRegistrationListNode(items=result, total_count=len(result))

    def get_student_current_registered_exam(self, student_uid) -> StudentExamRegistration:
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

    def get_student_exam_to_register(self, student_uid) -> ExamToRegister:
        scr = aliased(StudentCourseRegistration)
        ser = aliased(StudentExamRegistration)

        # Query for course registrations not present in StudentExamRegistration
        with session_scope() as session:
            query = session.query(scr).outerjoin(ser, ser.student_course_registration_id == scr.id).filter(
                scr.student_uid == student_uid, ser.id.is_(None))

            # Execute the query and get the results
            first_sitting = query.all()
            postponed_exams = session.query(StudentCourseRegistration). \
                join(StudentExamPostponement) \
                .filter(StudentExamPostponement.is_resumed == False, StudentExamPostponement.deleted_at.is_(None)) \
                .filter(StudentCourseRegistration.student_uid == student_uid).all()

            failure_exams = session.query(StudentCourseRegistration). \
                join(StudentExamRegistration) \
                .join(StudentExamFailure) \
                .filter(StudentExamFailure.is_attended == False, StudentExamFailure.deleted_at.is_(None)) \
                .filter(StudentCourseRegistration.student_uid == student_uid).all()

            return ExamToRegister(
                first_sitting=first_sitting,
                failure=failure_exams,
                postponed=postponed_exams
            )

    def upload_online_score(self, inputs) -> UploadResponse:
        exam_category_id = inputs.exam_category_id
        assessment_number = inputs.assessment_number
        out_off = float(inputs.out_off)
        program_course_id = inputs.program_course_id
        weight = inputs.weight
        source = inputs.source

        # print("Online marks input", inputs)

        with session_scope() as session:
            is_ue = session.query(ExamCategory).filter(
                ExamCategory.id == exam_category_id).first().is_ue
            # get student list from uaa service to get student uid after filtering

            reg_numbers = []  # Initialize an empty list to store registration numbers
            for row in inputs.marks:
                reg_number_ = row.registration_number
                reg_numbers.append(reg_number_)  # Append the registration number to the list

            # Now reg_numbers contains all the registration numbers from the specified worksheet rows

            students = get_student_from_uaa_by_reg_numbers(reg_numbers)

            # students = get_student_from_uaa()
            success = 0
            failed = 0
            failed_students = []
            success_students = []

            for row in inputs.marks:
                if row.score is None:
                    continue

                reg_number = row.registration_number

                try:
                    score = float(row.score)
                except ValueError:
                    score = 'InvalidMarks'
                # score = float(row.score)

                # program_course = session.query(ProgramCourse).filter(ProgramCourse.id == program_course_id,
                #                                                      ProgramCourse.deleted_at.is_(None)).first()
                #
                # exam_category = session.query(ExamCategory).filter(ExamCategory.id == exam_category_id,
                #                                                    ExamCategory.deleted_at.is_(None)).first()

                success_, failed_, failed_student, success_student = general_upload(students=students,
                                                                                    program_course_id=program_course_id,
                                                                                    exam_category_id=exam_category_id,
                                                                                    score=score,
                                                                                    out_off=out_off, weight=weight,
                                                                                    is_ue=is_ue,
                                                                                    reg_number=reg_number,
                                                                                    assessment_number=assessment_number,
                                                                                    source=source,
                                                                                    course_code=''
                                                                                    )
                success = success + success_
                failed = failed + failed_
                if failed_student.reg_number is not None:
                    failed_students.append(failed_student)
                if success_student.reg_number is not None:
                    success_students.append(success_student)
            response_data = UploadResponse(
                success=success,
                failed=failed,
                failed_students=failed_students,
                success_students=success_students
            )

            headers = {
                "Content-Type": "application/json"
            }

            payload = {
                "email": "husseinmkwazu@sua.ac.tz",
                "course_code": "DIT0105"
            }
            print("kabla uaaaaaaa: ", payload)
            response = requests.post(settings.UAA_URi + '/course/upload/status', json=payload, headers=headers,
                                     timeout=5)
            print("baada uaaaaaaaaaa: ")

            if response.status_code != 200:
                print("imefeli kutuma email")

            return response_data
