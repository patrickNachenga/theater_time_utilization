import dataclasses
import re
from typing import List

import requests
from passlib.context import CryptContext
from sqlalchemy import and_, desc

from src.core.config import settings
from src.core.moodle_api import MoodleApi
from src.core.security import Info
from src.db.session import session_scope
from src.models import Course
from src.modules.course.service import CourseService
from src.modules.program_course.service import ProgramCourseService

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


"""
Create program_course to moodleComputer Application
"""


def create_group_to_moodle():
    with session_scope() as session:
        # Get only one at a time
        course = CourseService.get_register_moodle_course()
        if course:
            try:
                # If there are existing course check for program course it belong that has null moodle id
                program_course = ProgramCourseService.get_unregister_moodle_program_course_by_course_id(course.id)
                if program_course:
                    # Attempt to create_group to moodle
                    moodle = MoodleApi()
                    moodle_unit_id = moodle.create_group(
                        course_id=course.id,
                        group_name=program_course.program_semester.academic_year.name,
                        group_description=program_course.program_semester.semester,
                    )
                    if moodle_unit_id != 0:
                        programCourse = ProgramCourseService.get_program_course_by_uid(program_course.uid)
                        if programCourse:
                            programCourse.moodle_id = moodle_unit_id
                            session.add(programCourse)
                            session.commit()
                            print(
                                '--- %s group  Successfully Generated to Moodle ---' % program_course.program_semester.academic_year.name)
                        else:
                            print('--- Failure to Save Moodle id to registration Service. ID: %s  --- ', moodle_unit_id)
                    else:
                        print('--- Failure to create group to Moodle --- ')
            except Exception as e:
                print('--- An Exception Occurred While create group to Moodle --- ', course.code)
