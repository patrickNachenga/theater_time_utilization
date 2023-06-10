from typing import List

from src.db.session import session_scope
from src.models import ProgramSemester
from src.models.semester_registration import SemesterRegistration
from src.modules import CRUDBase
from src.types import SemesterRegistrationNode, SemesterRegistrationListNode


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
