import dataclasses
import re
from typing import List

import requests
from passlib.context import CryptContext
from sqlalchemy import and_, desc, exists

from src.core.config import settings
from src.core.moodle_api import MoodleApi
from src.core.security import Info
from src.db.session import session_scope
from src.models import Course, ProgramCourse, ProgramSemester, StudentCourseRegistration, CourseAllocation

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
                    if responseData and responseData["data"]['moodle_id']:
                        moodle = MoodleApi()
                        enrollment_status: bool = moodle.enroll_user_as_user(
                            user_id=responseData["data"]['moodle_id'],
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
                    if responseData and responseData["data"]['moodle_id']:
                        moodle = MoodleApi()
                        enrollment_status: bool = moodle.enroll_user_as_user(
                            user_id=responseData["data"]['moodle_id'],
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
                    if responseData and responseData["data"]['moodle_id']:
                        moodle = MoodleApi()
                        enrollment_status: bool = moodle.add_member_to_group(
                            user_id=responseData["data"]['moodle_id'],
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


