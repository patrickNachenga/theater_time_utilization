from datetime import datetime
from typing import List

from sqlalchemy.orm import aliased

from src.db.session import session_scope
from src.models import ProgramSemester, AcademicYear, StudentCourseRegistration, ProgramCourse
from src.models.semester_registration import SemesterRegistration
from src.modules import CRUDBase
from src.modules.academic_year.service import AcademicYearCrud
from src.types import SemesterRegistrationNode, SemesterRegistrationListNode
from sqlalchemy import create_engine, text, and_, func, case, literal_column


class SemesterRegistrationService(object):
    @staticmethod
    def get_semester_registrations(pagination) -> SemesterRegistrationListNode:
        return CRUDBase(SemesterRegistration).get_multi_paginated(pagination, ['student_uid'],
                                                                  SemesterRegistrationListNode)

    @staticmethod
    def get_student_semester_registrations(student_uid: str) -> List[SemesterRegistrationNode]:
        with session_scope() as session:
            result = session.query(SemesterRegistration).filter(SemesterRegistration.student_uid == student_uid,
                                                                SemesterRegistration.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_active_year_student_semester_registrations():
        with (session_scope() as session):
            current_academic_year = session.query(AcademicYear).filter(AcademicYear.status == 1).first()
            if current_academic_year is None:
                return []
            current_month = int(datetime.now().strftime('%m'))
            semesters = ['10', '11', '12', '01', '02', '03']
            is_odd_semester = str(current_month).zfill(2) in semesters
            result = session.query(StudentCourseRegistration.student_uid,
                                   case([(ProgramSemester.semester % 2 == 0, literal_column('2'))],
                                        else_=literal_column('1')).label('semester'),
                                   func.count().label('registration_count')). \
                join(ProgramCourse, ProgramCourse.id == StudentCourseRegistration.program_course_id).join(
                ProgramSemester, ProgramSemester.id == ProgramCourse.program_semester_id). \
                filter(
                and_(
                    ProgramSemester.academic_year.has(id=current_academic_year.id),
                    StudentCourseRegistration.deleted_at.is_(None),
                    ProgramSemester.semester % 2 == (1 if is_odd_semester else 0)
                )
            ).group_by(StudentCourseRegistration.student_uid, ProgramSemester.semester).all()

            # registered_studentss = session.query(StudentCourseRegistration.student_uid).join() .filter().limit(20).all()
            # print(registered_studentss)
            return {
                'academic_year': current_academic_year.name,
                'student_uids': result
            }

    def register_student_semester(self, inputs) -> bool:
        """
        Register Student to semester
        :param inputs:
        :return:
        """

        with session_scope() as session:
            semester_program = session.query(ProgramSemester).filter(ProgramSemester.uid == inputs.program_semester_uid,
                                                                     ProgramSemester.deleted_at.is_(None)).first()
            # Check if program semester already exist
            if semester_program is None:
                return False
            semester_registration = SemesterRegistration(
                student_uid=inputs.student_uid,
                study_year=inputs.student_uid,
                semester_program=semester_program
            )
            session.add_all(semester_registration)
            session.commit()
            return True

    @staticmethod
    def get_registered_students() -> bool:
        # Create the SQLAlchemy engine for the first database (Server 1)
        engine1 = create_engine("postgresql://postgres:Sua123@45.61.55.203:5434/registration_db")

        # Create the SQLAlchemy engine for the second database (Server 2)
        engine2 = create_engine("postgresql://postgres:Sua123@45.61.55.203/uaa_db")
        conn1 = engine1.connect()
        conn2 = engine2.connect()
        sql_query = text("""
            SELECT sr.study_year, sr.student_uid, st.registration_number
            FROM semester_registrations sr
            JOIN dblink('host=45.61.55.203 port=5433 user=postgres password=Sua123 dbname=uaa_db',
                        'SELECT uid, registration_number FROM students') AS st(uid TEXT, registration_number TEXT)
            ON sr.student_uid = st.uid
           
        """)
        result = conn1.execute(sql_query)
        for row in result:
            study_year, student_uid, registration_number = row
            print(
                f"Study Year: {study_year}, Student UID: {student_uid}, Registration Number: {registration_number}")

        return True

    @staticmethod
    def get_registered_students_plan_B() -> bool:
        with session_scope() as session:
            semester_registrations = session.query(SemesterRegistration).filter(
                SemesterRegistration.deleted_at.is_(None))
            return semester_registrations
