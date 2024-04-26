import dataclasses
import math
import re
from typing import List

import requests
from passlib.context import CryptContext
from sqlalchemy import and_, desc, exists, func
from sqlalchemy.orm import aliased

from src.core.config import settings
from src.core.moodle_api import MoodleApi
from src.core.security import Info
from src.db.session import session_scope
from src.models import Course, ProgramCourse, ProgramSemester, StudentCourseRegistration, CourseAllocation, \
    AcademicYear, AcademicYearSemester, ExamCoursework, ExamCategory, ExamResult, ProgramCourseAssessment, \
    ExamResultSummary, ByLaw, Process, State, TransitionMeta
from src.modules.by_law.by_law_classes import BYLAW
from src.modules.by_law.service import ByLawService
from src.types import UploadResponse, FailedStudent, SuccessStudent

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def dataclass_from_dict(klass, d):
    try:
        fieldtypes = {f.name: f.type for f in dataclasses.fields(klass)}
        return klass(**{f: dataclass_from_dict(fieldtypes[f], d[f]) for f in d})
    except:
        return d  # Not a dataclass field


def decode_ldap_attributes(ldap_string):
    return ldap_string[0].decode('ASCII')


def camel_to_snake(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def auth_user_has_permission(info: Info, required_permissions: List[str]):
    """
    Check if login user has supplied permissions
    """
    if info.context.user:
        for perm in required_permissions:
            print(info.context.user.authorities)
            if perm in info.context.user.authorities:
                return True
    return False


def create_course_to_moodle():
    with session_scope() as session:
        # Get only one at a time
        course = session.query(Course).filter(
            and_(Course.moodle_id.is_(None), (Course.moodle_check_status.is_(False)),
                 Course.deleted_at.is_(None))).order_by(desc(Course.created_at)).first()
        if course:
            """
            Call Department moodle id for uuid
            """
            try:
                response = requests.get(settings.UAA_URi + f"/department/{course.department_uid}", timeout=5)
                if response.status_code == 200:
                    responseData = response.json()
                    if responseData["status"] and responseData["data"]['moodle_id'] is not None:
                        # update moodle course only if department found
                        moodle = MoodleApi()
                        moodle_unit_id = moodle.createCourse(
                            departmentId=responseData["data"]['moodle_id'],
                            courseFullName=course.name,
                            courseDescription=course.description,
                            courseShortName=course.code,
                        )
                        if moodle_unit_id != 0:
                            course.moodle_id = moodle_unit_id
                        else:
                            print('--- Failure to create course to Moodle --- ', moodle_unit_id)
                    course.moodle_check_status = True
                    session.add(course)
                    session.commit()
            except Exception as e:
                print('--- Exception Occurred while adding Course to Moodle. course ', str(e))
        else:
            """
            checking leach the end. now reset all course moodle_check_status to False
            """
            courses = session.query(Course).filter(
                and_(Course.moodle_id.is_(None), (Course.moodle_check_status.is_(True)),
                     Course.deleted_at.is_(None))).order_by(desc(Course.created_at)).all()
            if courses:
                for course in courses:
                    course.moodle_check_status = False
                    session.add(course)
                session.commit()
                print('--- RELOAD: create course to Moodle Service restart again --- ')


def create_group_to_moodle():
    with session_scope() as session:
        try:
            # Get only one at a time
            program_course: ProgramCourse = session.query(ProgramCourse).join(Course).join(ProgramSemester) \
                .filter(ProgramCourse.moodle_id.is_(None)) \
                .filter(ProgramCourse.course.has(Course.moodle_id.isnot(None))) \
                .order_by(desc(ProgramCourse.created_at)) \
                .first()
            if program_course:
                # Attempt to create_group to moodle
                moodle = MoodleApi()

                moodle_unit_id = moodle.create_group(
                    course_id=program_course.course.moodle_id,
                    group_name=f"{program_course.program_semester.program.code} {program_course.course.code} {program_course.program_semester.academic_year.name} Semester {program_course.program_semester.semester}",
                    group_description=program_course.program_semester.semester,
                )
                if moodle_unit_id != 0:
                    program_course.moodle_id = moodle_unit_id
                    session.add(program_course)
                    session.commit()
                else:
                    print('--- Failure to create group to Moodle. Moodle return 0 --- ')
        except Exception as e:
            print('--- Exception Occurred while adding Groups to Moodle.  ', str(e))


def enroll_student_to_moodle_course():
    with session_scope() as session:
        try:
            # Get data that student course registration not on moodle and program course already on moodle
            student_course_registration: StudentCourseRegistration = session.query(StudentCourseRegistration).join(
                ProgramCourse) \
                .filter(StudentCourseRegistration.moodle_course_enrollment_status.is_(False)) \
                .filter(StudentCourseRegistration.moodle_student_course_enrollment_status.is_(False)) \
                .filter(StudentCourseRegistration.program_course.has(ProgramCourse.moodle_id.isnot(None))) \
                .order_by(desc(StudentCourseRegistration.created_at)) \
                .first()
            if student_course_registration:
                params = {"uid": student_course_registration.student_uid}
                response = requests.get(settings.UAA_URi + f'/users/student', params=params, timeout=5)

                response.raise_for_status()
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data and response_data["user"]['moodle_id']:
                        moodle = MoodleApi()
                        enrollment_status: bool = moodle.enroll_user_as_user(
                            user_id=response_data["user"]['moodle_id'],
                            course_id=student_course_registration.program_course.course.moodle_id,
                            role_name="student",
                        )
                        if enrollment_status:
                            student_course_registration.moodle_course_enrollment_status = True
                            print(f'--- Successful Enroll Student : {response_data["user"]["username"]} to Moodle '
                                  f'Course --- on course_allocation:')
                        else:
                            print('--- Fail to Enroll Student to Moodle Course --- on student_course_registration_uid:',
                                  student_course_registration.uid)
                    else:
                        if response_data["user"]:
                            print(f'--- User Wait to be registered on Moodle  user:{response_data["user"]["username"]}')
                        else:
                            print(f'--- User Not Found  -----', params)

                student_course_registration.moodle_student_course_enrollment_status = True
                session.add(student_course_registration)
                session.commit()
            else:
                """
                checking leach the end. now reset all moodle_student_course_enrollment_status to False
                """
                student_course_registrations = session.query(StudentCourseRegistration).join(
                    ProgramCourse) \
                    .filter(StudentCourseRegistration.moodle_course_enrollment_status.is_(False)) \
                    .filter(StudentCourseRegistration.moodle_student_course_enrollment_status.is_(True)) \
                    .filter(StudentCourseRegistration.program_course.has(ProgramCourse.moodle_id.isnot(None))) \
                    .order_by(desc(StudentCourseRegistration.created_at)) \
                    .all()
                if student_course_registrations:
                    for student_course_registration in student_course_registrations:
                        student_course_registration.moodle_student_course_enrollment_status = False
                        session.add(student_course_registration)
                    session.commit()
                    print('--- RELOAD: Enroll student to Moodle Course  Service restarted Again ---')
        except Exception as e:
            print('--- Exception Occurred while enrolling student to Moodle.  ', str(e))


def unroll_student_to_moodle_course():
    with session_scope(withDeleted=True) as session:
        try:
            # Get data that student course registration not on moodle and program course already on moodle
            student_course_registration: StudentCourseRegistration = session.query(StudentCourseRegistration) \
                .filter(StudentCourseRegistration.moodle_course_enrollment_status.is_(True)) \
                .filter(StudentCourseRegistration.deleted_at.isnot(None)) \
                .order_by(desc(StudentCourseRegistration.deleted_at)) \
                .first()
            if student_course_registration:
                params = {"uid": student_course_registration.student_uid}
                response = requests.get(settings.UAA_URi + f'/users/student', params=params, timeout=5)
                response.raise_for_status()
                if response.status_code == 200:
                    responseData = response.json()
                    if responseData and responseData["user"]['moodle_id']:
                        moodle = MoodleApi()
                        enrollment_status: bool = moodle.unroll_user_from_course(
                            userId=responseData["user"]['moodle_id'],
                            courseId=student_course_registration.program_course.course.moodle_id,
                            roleName="student",
                        )
                        if enrollment_status:
                            student_course_registration.moodle_course_enrollment_status = False
                            session.add(student_course_registration)
                            session.commit()
                        else:
                            print('--- Fail to Enroll Student to Moodle Course --- on student_course_registration_uid:',
                                  student_course_registration.uid)
        except Exception as e:
            print('--- Exception Occurred while enrolling student to Moodle.  ', str(e))


def enroll_staff_to_moodle_course():
    with session_scope() as session:
        try:
            # Get data that course allocation not on moodle and program course already on moodle
            course_allocation: CourseAllocation = session.query(CourseAllocation).join(ProgramCourse) \
                .filter(CourseAllocation.moodle_course_enrollment_status.is_(False)) \
                .filter(CourseAllocation.moodle_staff_course_enrollment_status.is_(False)) \
                .filter(CourseAllocation.program_course.has(ProgramCourse.moodle_id.isnot(None))) \
                .order_by(desc(CourseAllocation.created_at)) \
                .first()
            if course_allocation:
                # check if this staff already enrolled to this moodle course
                staff_course_allocation: CourseAllocation = session.query(CourseAllocation) \
                    .join(ProgramCourse).join(Course) \
                    .filter(CourseAllocation.staff_uid == course_allocation.staff_uid) \
                    .filter(
                    CourseAllocation.program_course.has(Course.id == course_allocation.program_course.course.id)) \
                    .filter(CourseAllocation.program_course_id != course_allocation.program_course.id) \
                    .filter(CourseAllocation.moodle_course_enrollment_status.is_(True)) \
                    .order_by(desc(CourseAllocation.created_at)) \
                    .first()
                if not staff_course_allocation:
                    params = {"uid": course_allocation.staff_uid}
                    response = requests.get(settings.UAA_URi + f'/users/staff', params=params, timeout=5)
                    response.raise_for_status()
                    if response.status_code == 200:
                        responseData = response.json()
                        if responseData and responseData['user']['moodle_id']:
                            moodle = MoodleApi()
                            enrollment_status = moodle.enroll_user_as_user(
                                user_id=responseData['user']['moodle_id'],
                                course_id=course_allocation.program_course.course.moodle_id,
                                role_name="editingteacher",
                            )
                            if enrollment_status:
                                course_allocation.moodle_course_enrollment_status = True
                                print(f'--- Successful Enroll Teacher : {responseData["user"]["username"]} to Moodle '
                                      f'Course --- on course_allocation:')
                            else:
                                print('--- Fail to Enroll Teacher to Moodle Course --- on course_allocation:',
                                      course_allocation.uid)
                course_allocation.moodle_staff_course_enrollment_status = True
                session.add(course_allocation)
                session.commit()
            else:
                """
                checking leach the end. now reset all moodle_staff_course_enrollment_status to False
                """
                course_allocations = session.query(CourseAllocation).join(ProgramCourse) \
                    .filter(CourseAllocation.moodle_course_enrollment_status.is_(False)) \
                    .filter(CourseAllocation.moodle_staff_course_enrollment_status.is_(True)) \
                    .filter(CourseAllocation.program_course.has(ProgramCourse.moodle_id.isnot(None))) \
                    .order_by(desc(CourseAllocation.created_at)).all()
                if course_allocations:
                    for course_allocation in course_allocations:
                        course_allocation.moodle_staff_course_enrollment_status = False
                        session.add(course_allocation)
                    session.commit()
                    print('--- RELOAD: Enroll staff to Moodle Course  Service restarted Again ---')

        except Exception as e:
            print('--- Exception Occurred while enrolling Teacher to Moodle Course.  ', str(e))


def enroll_student_to_moodle_group():
    with session_scope() as session:
        try:
            # Get data that student group registration not on moodle and program course already on moodle
            student_course_registration: StudentCourseRegistration = session.query(StudentCourseRegistration).join(
                ProgramCourse) \
                .filter(StudentCourseRegistration.moodle_course_enrollment_status.is_(True)) \
                .filter(StudentCourseRegistration.moodle_group_enrollment_status.is_(False)) \
                .filter(StudentCourseRegistration.program_course.has(ProgramCourse.moodle_id.isnot(None))) \
                .order_by(desc(StudentCourseRegistration.created_at)) \
                .first()

            if student_course_registration:
                params = {"uid": student_course_registration.student_uid}
                response = requests.get(settings.UAA_URi + f'/users/student', params=params, timeout=5)
                response.raise_for_status()
                if response.status_code == 200:
                    responseData = response.json()
                    if responseData and responseData['user']['moodle_id']:
                        moodle = MoodleApi()
                        enrollment_status: bool = moodle.add_member_to_group(
                            user_id=responseData['user']['moodle_id'],
                            group_id=student_course_registration.program_course.moodle_id,
                        )
                        if enrollment_status:
                            student_course_registration.moodle_group_enrollment_status = True
                            session.add(student_course_registration)
                            session.commit()
                            print(f'--- Successful Enroll Student:{responseData["user"]["username"]} to Moodle Group')
                        else:
                            print('--- Fail to Enroll Student to Moodle Group --- on student_course_registration_uid:',
                                  student_course_registration.uid)
        except Exception as e:
            print('--- Exception Occurred while enrolling student to Group.  ', str(e))


def enroll_staff_to_moodle_group():
    with session_scope() as session:
        try:
            # Get data that student group registration not on moodle and program course already on moodle
            staff_course_allocation: CourseAllocation = session.query(CourseAllocation).join(ProgramCourse) \
                .filter(CourseAllocation.moodle_course_enrollment_status.is_(True)) \
                .filter(CourseAllocation.moodle_group_enrollment_status.is_(False)) \
                .filter(CourseAllocation.program_course.has(ProgramCourse.moodle_id.isnot(None))) \
                .order_by(desc(CourseAllocation.created_at)) \
                .first()

            if staff_course_allocation:
                params = {"uid": staff_course_allocation.staff_uid}
                response = requests.get(settings.UAA_URi + f'/users/staff', params=params, timeout=5)
                response.raise_for_status()
                if response.status_code == 200:
                    responseData = response.json()
                    if responseData and responseData['user']['moodle_id']:
                        moodle = MoodleApi()
                        enrollment_status: bool = moodle.add_member_to_group(
                            user_id=responseData['user']['moodle_id'],
                            group_id=staff_course_allocation.program_course.moodle_id,
                        )
                        if enrollment_status:
                            staff_course_allocation.moodle_group_enrollment_status = True
                            session.add(staff_course_allocation)
                            session.commit()
                        else:
                            print('--- Fail to Enroll Staff to Moodle Group --- on staff_course_allocation_uid:',
                                  staff_course_allocation.uid)
        except Exception as e:
            print('--- Exception Occurred while enrolling staff to Group.  ', str(e))


def get_current_semester():
    with session_scope() as session:
        semester = None
        current_academic_year = session.query(AcademicYear).filter(AcademicYear.status == 1).first()
        if current_academic_year:
            academic_year_semester = session.query(AcademicYearSemester).filter(
                AcademicYearSemester.academic_year == current_academic_year).first()
        if academic_year_semester:
            semester = academic_year_semester.semester
        return semester


def get_current_academic_year():
    with session_scope() as session:
        name = None
        current_academic_year = session.query(AcademicYear).filter(AcademicYear.status == 1).first()
        if current_academic_year:
            name = current_academic_year.name

        return name


def get_user_departments_headship(info: Info):
    c_list = []
    u_list = []
    d_list = []
    if len(info.context.user.campus_headships) > 0:
        try:
            url = f"{settings.UAA_URi}/departments/campuses"
            # url = "http://127.0.0.1:8000/departments/campuses"
            response = requests.post(url, json=info.context.user.campus_headships, timeout=5)
            c_list = response.json()
            # print('c_list', c_list)
        except Exception as e:
            print(e)
    if len(info.context.user.unit_headships) > 0:
        try:
            url = f"{settings.UAA_URi}/departments/units"
            # url = "http://127.0.0.1:8000/departments/units"
            response = requests.post(url, json=info.context.user.unit_headships, timeout=5)
            u_list = response.json()
        except Exception as e:
            print(e)
    if len(info.context.user.department_headships) > 0:
        d_list = info.context.user.department_headships
    combined_list = set(c_list + u_list + d_list)

    return combined_list


def get_user_programs_headship(info: Info):
    user_program_uids = []
    if len(info.context.user.program_headships) > 0:
        user_program_uids = info.context.user.program_headships

    return user_program_uids


def insert_course_work(registration_number, first_name, middle_name, last_name, gender, student_uid, program_course_id,
                       exam_category_id, assessment_number, out_off, score,
                       weight, source, by_law_uid):
    with session_scope() as session:

        try:
            program_course = session.query(ProgramCourse).filter(ProgramCourse.id == program_course_id,
                                                                 ProgramCourse.deleted_at.is_(None)).first()
            exam_category = session.query(ExamCategory).filter(ExamCategory.id == exam_category_id,
                                                               ExamCategory.deleted_at.is_(None)).first()
            exam_course_work = session.query(ExamCoursework).filter(ExamCoursework.student_uid == student_uid,
                                                                    ExamCoursework.program_course == program_course,
                                                                    ExamCoursework.exam_category == exam_category,
                                                                    ExamCoursework.assessment_number == assessment_number).first()
            score = (score / out_off) * 100
            if exam_course_work:
                exam_course_work.score = custom_round(score)
                exam_course_work.weight = weight
                exam_course_work.source = source
                instance = exam_course_work
            else:
                new_exam_coursework = ExamCoursework(
                    student_uid=student_uid,
                    exam_category=exam_category,
                    program_course=program_course,
                    assessment_number=assessment_number,
                    score=custom_round(score),
                    weight=weight,
                    source=source
                )
                session.add(new_exam_coursework)
                instance = new_exam_coursework
            session.commit()
            attach_coursework_listener(target=instance, registration_number=registration_number, first_name=first_name,
                                       middle_name=middle_name, last_name=last_name, gender=gender,
                                       by_law_uid=by_law_uid)

            return True, "successfully"
        except Exception as e:
            print(e)
            return False, "Data Processing Error in Exception"


def insert_exam_result(student_uid, program_course_id, exam_category_id, score, out_off, weight, by_law_uid, source):
    with session_scope() as session:

        is_inserted = are_minimum_course_work_exams_inserted(session, program_course_id, student_uid)
        if is_inserted:
            try:
                program_course = session.query(ProgramCourse).filter(ProgramCourse.id == program_course_id,
                                                                     ProgramCourse.deleted_at.is_(None)).first()
                exam_category = session.query(ExamCategory).filter(ExamCategory.id == exam_category_id,
                                                                   ExamCategory.deleted_at.is_(None)).first()
                exam_result = session.query(ExamResult).filter(ExamResult.student_uid == student_uid,
                                                               ExamResult.program_course == program_course,
                                                               ExamResult.exam_category == exam_category).first()
                score = (score / out_off) * 100
                if exam_result:
                    exam_result.score = score
                    exam_result.weight = weight
                    exam_result.source = source
                    instance = exam_result
                else:
                    new_exam_result = ExamResult(
                        student_uid=student_uid,
                        exam_category=exam_category,
                        program_course=program_course,
                        score=score,
                        weight=weight,
                        source=source
                    )

                    session.add(new_exam_result)
                    instance = new_exam_result
                session.commit()
                attach_exam_result_listener(target=instance, by_law_uid=by_law_uid)
                return True, "Successfully"
            except Exception as e:
                print(e)
                return False, "Data processing error"
        else:
            return False, "Can not Upload UE, Other course works assessment not yet uploaded"


def get_student_from_uaa():
    try:

        # Set the Content-Type header to indicate that the request body is JSON
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.get(settings.UAA_URi + '/users/students', headers=headers, timeout=5)

    except Exception as e:
        print('excption occurred', e)
        response = None
    if response.status_code == 200:
        data = response.json()
        return data


def general_upload(students=None, program_course_id=None, exam_category_id=None, score=None, out_off=None, weight=None,
                   is_ue=None, reg_number=None, assessment_number=None, source='Excel', ):
    success = 0
    failed = 0
    failed_student = FailedStudent(reg_number=None, reason=None)
    success_student = SuccessStudent(reg_number=None)

    if students:

        matching_item = next(
            (item for item in students if item["registration_number"] == reg_number), None)
        if matching_item:
            student_uid = matching_item["uid"]
            registration_number = matching_item["registration_number"]
            by_law_uid = matching_item["bylaw_uid"]
            first_name = matching_item["user"]["first_name"]
            middle_name = matching_item["user"]["middle_name"]
            last_name = matching_item["user"]["last_name"]
            gender = matching_item["user"]["gender"]

            if not by_law_uid:
                failed = failed + 1
                failed_student.reg_number = reg_number
                failed_student.reason = "Student has no by-law"
            else:

                if score is None:
                    score = 0

                if score <= out_off:
                    if is_ue:
                        result, reason = insert_exam_result(student_uid, program_course_id, exam_category_id, score,
                                                            out_off,
                                                            weight, by_law_uid, source)
                        if result:
                            success = success + 1
                            success_student.reg_number = reg_number
                        else:
                            failed = failed + 1
                            failed_student.reg_number = reg_number
                            failed_student.reason = reason
                    else:
                        result, reason = insert_course_work(registration_number, first_name, middle_name, last_name,
                                                            gender,
                                                            student_uid, program_course_id, exam_category_id,
                                                            assessment_number,
                                                            out_off, score,
                                                            weight, source, by_law_uid)
                        if result:
                            success = success + 1
                            success_student.reg_number = reg_number

                        else:
                            failed = failed + 1
                            failed_student.reg_number = reg_number
                            failed_student.reason = reason

                else:
                    failed = failed + 1
                    failed_student.reg_number = reg_number
                    failed_student.reason = "Score is greater than " + str(out_off)
        else:
            failed = failed + 1
            failed_student.reg_number = reg_number
            failed_student.reason = "Data processing error ,student not found"

    else:
        failed = failed + 1
        failed_student.reg_number = reg_number
        failed_student.reason = "Data processing error , UAA service not found"

    return success, failed, failed_student, success_student


def attach_coursework_listener(target, registration_number, first_name, middle_name, last_name, gender, by_law_uid):
    # def coursework_after_insert_or_update(mapper, connection, target):
    with session_scope() as session:

        student_exam_course_works = session.query(ExamCoursework).filter(
            ExamCoursework.student_uid == target.student_uid,
            ExamCoursework.program_course_id == target.program_course_id)
        total_practical_score = 0
        total_theory_score = 0
        program_type = student_exam_course_works.first().program_course.program_semester.program.program_category.short_name
        for exam_course_work in student_exam_course_works:

            maximum_score = session.query(ProgramCourseAssessment.maximum_score).filter(
                ProgramCourseAssessment.exam_category_id == exam_course_work.exam_category_id,
                ProgramCourseAssessment.program_course_id == exam_course_work.program_course_id).scalar()

            total_weight = session.query(func.coalesce(func.sum(ExamCoursework.weight))).filter(
                ExamCoursework.student_uid == target.student_uid,
                ExamCoursework.exam_category_id == exam_course_work.exam_category_id,
                ExamCoursework.program_course_id == target.program_course_id).scalar()
            weighted_score = (exam_course_work.score / 100) * maximum_score * (exam_course_work.weight / total_weight)
            if exam_course_work.exam_category.is_theory:
                total_theory_score += weighted_score
            else:
                total_practical_score += weighted_score

            total_score = total_theory_score + total_practical_score

        exam_result_summary = session.query(ExamResultSummary).filter(
            ExamResultSummary.student_uid == target.student_uid,
            ExamResultSummary.program_course_id == target.program_course.id,
            ExamResultSummary.number_of_sitting == 1).first()
        if exam_result_summary:

            exam_result_summary.cw_score = custom_round(total_score)
            if total_theory_score > 0:
                exam_result_summary.cw_theory = custom_round(total_theory_score)

            if total_practical_score > 0:
                exam_result_summary.cw_practical = custom_round(
                    total_practical_score)
            if exam_result_summary.cw_score and exam_result_summary.ue_score:
                exam_result_summary.total_score = exam_result_summary.cw_score + exam_result_summary.ue_score

            summary_instance = exam_result_summary

        else:

            new_exam_result = ExamResultSummary(
                student_uid=target.student_uid,
                registration_number=registration_number,
                program_course_id=target.program_course.id,
                number_of_sitting=1,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                gender=gender,
                credit=target.program_course.credit,
                course_code=target.program_course.course.code,
                course_name=target.program_course.course.name,
                cw_practical=custom_round(total_practical_score),
                cw_theory=custom_round(total_theory_score),
                cw_score=custom_round(total_score),
                grade='I',
                grade_remark='Incomplete',
                exam_status=1,
                publish_status=False,
                study_year=target.program_course.program_semester.study_year,
                semester=target.program_course.program_semester.semester,
                academic_year_uid=target.program_course.program_semester.academic_year.uid,
                program_uid=target.program_course.program_semester.program.uid,
                course_category=target.program_course.course_category.name
            )
            summary_instance = new_exam_result
            session.add(new_exam_result)

        grade_result(session, target, by_law_uid, summary_instance, program_type)
        session.commit()


def attach_exam_result_listener(target, by_law_uid):
    with session_scope() as session:
        student_exam_results = session.query(ExamResult).filter(
            ExamResult.student_uid == target.student_uid,
            ExamResult.program_course_id == target.program_course_id,
            ExamResult.number_of_sitting == target.number_of_sitting)
        total_score = 0
        total_ue_theory = 0
        total_ue_practical = 0
        total_ue_oral = 0
        program_type = student_exam_results.first().program_course.program_semester.program.program_category.short_name
        for exam_result in student_exam_results:
            maximum_score = session.query(ProgramCourseAssessment.maximum_score).filter(
                ProgramCourseAssessment.exam_category_id == exam_result.exam_category_id,
                ProgramCourseAssessment.program_course_id == exam_result.program_course_id).scalar()
            total_weight = session.query(func.coalesce(func.sum(ExamResult.weight))).filter(
                ExamResult.student_uid == target.student_uid,
                ExamResult.exam_category_id == exam_result.exam_category_id,
                ExamResult.program_course_id == target.program_course_id,
                ExamResult.number_of_sitting == target.number_of_sitting).scalar()
            weighted_score = (exam_result.score / 100) * maximum_score * (exam_result.weight / total_weight)

            if exam_result.exam_category.is_theory:
                total_ue_theory += weighted_score
            elif exam_result.exam_category.is_theory:
                total_ue_oral += weighted_score

            else:
                total_ue_practical += weighted_score

            total_score = total_ue_theory + total_ue_practical + total_ue_oral

        exam_result_summary = session.query(ExamResultSummary).filter(
            ExamResultSummary.student_uid == target.student_uid,
            ExamResultSummary.program_course_id == target.program_course.id,
            ExamResultSummary.number_of_sitting == target.number_of_sitting).first()
        if exam_result_summary:

            exam_result_summary.ue_theory = custom_round(total_ue_theory)
            exam_result_summary.ue_practical = custom_round(total_ue_practical)
            exam_result_summary.ue_oral = custom_round(total_ue_oral)
            exam_result_summary.ue_score = custom_round(total_score)
            exam_result_summary.total_score = exam_result_summary.cw_score + exam_result_summary.ue_score
            grade_result(session, target, by_law_uid, exam_result_summary, program_type)

        else:
            pass
        session.commit()


def are_minimum_course_work_exams_inserted(session, program_course_id, student_uid):
    # Get a list of exam categories along with their minimum exams
    exam_categories_with_min_exams = (session.query(
        ProgramCourseAssessment.exam_category_id,
        ProgramCourseAssessment.minimum_exams
    ).join(ProgramCourse).filter(ProgramCourseAssessment.program_course.has(id=program_course_id),
                                 ProgramCourse.id == program_course_id,
                                 ~ProgramCourseAssessment.exam_category.has(is_ue=True)).all())

    for category_id, min_exams in exam_categories_with_min_exams:
        # Count the number of ExamCoursework entries for the specified ProgramCourse and ExamCategory
        exam_coursework_count = session.query(ExamCoursework).filter(ExamCoursework.exam_category_id == category_id,
                                                                     ExamCoursework.program_course_id == program_course_id,
                                                                     ExamCoursework.student_uid == student_uid).all()
        if len(exam_coursework_count) < min_exams:
            return False

    return True


def are_minimum_ue_exams_inserted(session, program_course_id, student_uid):
    # Get a list of exam categories along with their minimum exams
    exam_categories_with_min_exams = session.query(
        ProgramCourseAssessment.exam_category_id,
        ProgramCourseAssessment.minimum_exams
    ).join(ProgramCourse).filter(ProgramCourseAssessment.program_course.has(id=program_course_id),
                                 ProgramCourse.id == program_course_id,
                                 ProgramCourseAssessment.exam_category.has(is_ue=True)).all()

    for category_id, min_exams in exam_categories_with_min_exams:
        # Count the number of ExamCoursework entries for the specified ProgramCourse and ExamCategory
        exam_ue_count = session.query(ExamResult).filter(ExamResult.exam_category_id == category_id,
                                                         ExamResult.program_course_id == program_course_id,
                                                         ExamResult.student_uid == student_uid).all()

        if len(exam_ue_count) < min_exams:
            return False

    return True


def grade_result(session, target, by_law_uid, exam_result_summary, program_type):
    is_inserted = are_minimum_ue_exams_inserted(session, target.program_course_id, target.student_uid)
    if is_inserted:
        # perform grading by_law_uid
        by_law_code = ByLawService(ByLaw).get_by_law_by_uid(by_law_uid).code
        by_law = BYLAW[by_law_code]()
        performance_grade = by_law.get_course_performance_grade(exam_result_summary, program_type, session)
        exam_result_summary.grade = performance_grade['grade']
        exam_result_summary.grade_point = performance_grade['grade_point']
        exam_result_summary.grade_remark = performance_grade['status']
        exam_result_summary.grade_point_credit = exam_result_summary.credit * exam_result_summary.grade_point
        return exam_result_summary


def custom_round(value):
    return math.floor(value * 100) / 100


def can_progress(session, process: Process, new_state: State):
    # get the current process workflow
    workflow = process.workflow

    # Get current state
    current_state = process.current_state

    if not current_state:
        return True

    # Query Transition Meta Table for a record with matching workflow_id, source_state_id, destination_state_id
    transition = session.query(TransitionMeta) \
        .filter(and_(TransitionMeta.workflow_id == workflow.id,
                     TransitionMeta.source_state_id == current_state.state_id,
                     TransitionMeta.destination_state_id == new_state.state_id)) \
        .first()

    # If the query returns a TransitionMeta instance, we can transition from current state to new state
    if transition:
        return True
    else:
        return False
