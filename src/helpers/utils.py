import dataclasses
import re
from typing import List

import requests
from passlib.context import CryptContext
from sqlalchemy import and_, desc, exists, func

from src.core.config import settings
from src.core.moodle_api import MoodleApi
from src.core.security import Info
from src.db.session import session_scope
from src.models import Course, ProgramCourse, ProgramSemester, StudentCourseRegistration, CourseAllocation, \
    AcademicYear, AcademicYearSemester, ExamCoursework, ExamCategory, ExamResult, ProgramCourseAssessment, \
    ExamResultSummary
from src.types import UploadResponse, FailedStudent

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
            and_(Course.moodle_id.is_(None), Course.deleted_at.is_(None))).order_by(desc(Course.created_at)).first()
        if course:
            """
            Call Department moodle id for uuid
            """
            try:
                response = requests.get(settings.UAA_URi + f"/department/{course.department_uid}")
                if response.status_code == 200:
                    responseData = response.json()
                    if responseData["status"] and responseData["data"]['moodle_id']:
                        moodle = MoodleApi()
                        moodle_unit_id = moodle.createCourse(
                            departmentId=responseData["data"]['moodle_id'],
                            courseFullName=course.name,
                            courseDescription=course.description,
                            courseShortName=course.code,
                        )
                        if moodle_unit_id != 0:
                            course.moodle_id = moodle_unit_id
                            session.add(course)
                            session.commit()
                        else:
                            print('--- Failure to create course to Moodle --- ', moodle_unit_id)
            except Exception as e:
                print('--- Exception Occurred while adding Course to Moodle. course ', str(e))


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
                    group_name=f"{program_course.program_semester.academic_year.name} Semester {program_course.program_semester.semester}",
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
                .filter(StudentCourseRegistration.program_course.has(ProgramCourse.moodle_id.isnot(None))) \
                .order_by(desc(StudentCourseRegistration.created_at)) \
                .first()

            if student_course_registration:
                params = {"uid": student_course_registration.student_uid}
                response = requests.get(settings.UAA_URi + f'/users/student', params=params)
                response.raise_for_status()
                if response.status_code == 200:
                    responseData = response.json()
                    if responseData and responseData["user"]['moodle_id']:
                        moodle = MoodleApi()
                        enrollment_status: bool = moodle.enroll_user_as_user(
                            user_id=responseData["user"]['moodle_id'],
                            course_id=student_course_registration.program_course.course.moodle_id,
                            role_name="student",
                        )
                        if enrollment_status:
                            student_course_registration.moodle_course_enrollment_status = True
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
                .filter(CourseAllocation.moodle_enrollment_status.is_(False)) \
                .filter(CourseAllocation.program_course.has(ProgramCourse.moodle_id.isnot(None))) \
                .order_by(desc(CourseAllocation.created_at)) \
                .first()

            if course_allocation:
                params = {"uid": course_allocation.staff_uid}
                response = requests.get(settings.UAA_URi + f'/users/staff', params=params)
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
                            course_allocation.moodle_enrollment_status = True
                            session.add(course_allocation)
                            session.commit()
                        else:
                            print('--- Fail to Enroll Teacher to Moodle Course --- on course_allocation:',
                                  course_allocation.uid)
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
                response = requests.get(settings.UAA_URi + f'/users/student', params=params)
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
                        else:
                            print('--- Fail to Enroll Student to Moodle Group --- on student_course_registration_uid:',
                                  student_course_registration.uid)
        except Exception as e:
            print('--- Exception Occurred while enrolling student to Group.  ', str(e))


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
    if len(info.context.user.headships.campus_headships) > 0:
        try:
            url = f"{settings.UAA_URi}/departments/campuses"
            # url = "http://127.0.0.1:8000/departments/campuses"
            response = requests.post(url, json=info.context.user.headships.campus_headships)
            c_list = response.json()
            # print('c_list', c_list)
        except Exception as e:
            print(e)
    if len(info.context.user.headships.unit_headships) > 0:
        try:
            url = f"{settings.UAA_URi}/departments/units"
            # url = "http://127.0.0.1:8000/departments/units"
            response = requests.post(url, json=info.context.user.headships.unit_headships)
            u_list = response.json()
        except Exception as e:
            print(e)
    if len(info.context.user.headships.department_headships) > 0:
        d_list = info.context.user.headships.department_headships
    combined_list = set(c_list + u_list + d_list)

    return combined_list


def get_user_programs_headship(info: Info):
    user_program_uids = []
    if len(info.context.user.headships.program_headships) > 0:
        user_program_uids = info.context.user.headships.program_headships

    return user_program_uids


def insert_course_work(registration_number, first_name, middle_name, last_name, gender, student_uid, program_course_id,
                       exam_category_id, assessment_number, out_off, score,
                       weight) -> bool:
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
                exam_course_work.score = score
                exam_course_work.weight = weight
                instance = exam_course_work
            else:
                new_exam_coursework = ExamCoursework(
                    student_uid=student_uid,
                    exam_category=exam_category,
                    program_course=program_course,
                    assessment_number=assessment_number,
                    score=score,
                    weight=weight
                )
                session.add(new_exam_coursework)
                instance = new_exam_coursework
            session.commit()
            attach_coursework_listener(target=instance, registration_number=registration_number, first_name=first_name,
                                       middle_name=middle_name, last_name=last_name, gender=gender)

            return True
        except Exception as e:
            print(e)
            return False


def insert_exam_result(student_uid, program_course_id, exam_category_id, score, out_off, weight) -> bool:
    with session_scope() as session:
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
                instance = exam_result
            else:
                new_exam_result = ExamResult(
                    student_uid=student_uid,
                    exam_category=exam_category,
                    program_course=program_course,
                    score=score,
                    weight=weight
                )

                session.add(new_exam_result)
                instance = new_exam_result
            session.commit()
            attach_exam_result_listener(target=instance)
            return True
        except Exception as e:
            print(e)
            return False


def get_student_from_uaa():
    try:

        # Set the Content-Type header to indicate that the request body is JSON
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.get(settings.UAA_URi + '/users/students', headers=headers)

    except Exception as e:
        print('excption occurred', e)
        response = None
    if response.status_code == 200:
        data = response.json()
        return data


def general_upload(students=None, program_course_id=None, exam_category_id=None, score=None, out_off=None, weight=None,
                   is_ue=None, reg_number=None, assessment_number=None):
    success = 0
    failed = 0
    failed_student = FailedStudent(reg_number=None, reason=None)
    if students:
        matching_item = next(
            (item for item in students if item["registration_number"] == reg_number), None)
        if matching_item:
            student_uid = matching_item["uid"]
            registration_number = matching_item["registration_number"]
            first_name = matching_item["user"]["first_name"]
            middle_name = matching_item["user"]["middle_name"]
            last_name = matching_item["user"]["last_name"]
            gender = matching_item["user"]["gender"]
            if score <= out_off:
                if is_ue:
                    result = insert_exam_result(student_uid, program_course_id, exam_category_id, score,
                                                out_off,
                                                weight)
                    if result:
                        success = success + 1
                    else:
                        failed = failed + 1
                        failed_student.reg_number = reg_number
                        failed_student.reason = "Data processing error"
                else:
                    result = insert_course_work(registration_number, first_name, middle_name, last_name, gender,
                                                student_uid, program_course_id, exam_category_id,
                                                assessment_number,
                                                out_off, score,
                                                weight)
                    if result:
                        if result:
                            success = success + 1
                        else:
                            failed = failed + 1
                            failed_student.reg_number = reg_number
                            failed_student.reason = "Data processing error"

            else:
                failed = failed + 1
                failed_student.reg_number = reg_number
                failed_student.reason = "Score is greater than out off"
        else:
            failed = failed + 1
            failed_student.reg_number = reg_number
            failed_student.reason = "Data processing error ,student not found"

    else:
        failed = failed + 1
        failed_student.reg_number = reg_number
        failed_student.reason = "Data processing error , UAA service not found"

    return success, failed, failed_student


def attach_coursework_listener(target, registration_number, first_name, middle_name, last_name, gender):
    # def coursework_after_insert_or_update(mapper, connection, target):
    with session_scope() as session:

        student_exam_course_works = session.query(ExamCoursework).filter(
            ExamCoursework.student_uid == target.student_uid,
            ExamCoursework.program_course_id == target.program_course_id)
        total_practical_score = 0
        total_theory_score = 0

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
            exam_result_summary.cw_score = round(total_score, 2)
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
                cw_practical=round(total_practical_score, 2) if total_practical_score > 0 else None,
                cw_theory=round(total_theory_score, 2) if total_theory_score > 0 else None,
                cw_score=round(total_score, 2),
                grade='I',
                grade_remark='Incomplete',
                exam_status=1,
                publish_status=False,
                study_year=target.program_course.program_semester.study_year,
                semester=target.program_course.program_semester.semester,
                academic_year_id=target.program_course.program_semester.academic_year_id
            )
            session.add(new_exam_result)
        session.commit()


def attach_exam_result_listener(target):
    with session_scope() as session:
        student_exam_results = session.query(ExamResult).filter(
            ExamResult.student_uid == target.student_uid,
            ExamResult.program_course_id == target.program_course_id,
            ExamResult.number_of_sitting == target.number_of_sitting)
        total_score = 0
        total_ue_theory = 0
        total_ue_practical = 0

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
            else:
                total_ue_practical += weighted_score

            total_score = total_ue_theory + total_ue_practical
        exam_result_summary = session.query(ExamResultSummary).filter(
            ExamResultSummary.student_uid == target.student_uid,
            ExamResultSummary.program_course_id == target.program_course.id,
            ExamResultSummary.number_of_sitting == target.number_of_sitting).first()
        if exam_result_summary:
            exam_result_summary.ue_theory = round(total_ue_theory,2) if total_ue_theory else None
            exam_result_summary.ue_practical = round(total_ue_practical,2) if total_ue_practical else None
            exam_result_summary.ue_score = round(total_score, 2)

        session.commit()
