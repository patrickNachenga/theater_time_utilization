from typing import List

from sqlalchemy import select

from src.db.session import session_scope
from src.models import ProgramSemester
from src.models.staff import Staff
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramSemester, ProgramSemesterNode


class ProgramSemesterService(object):
    @staticmethod
    def get_program_semester() -> List[ProgramSemester]:
        with session_scope() as session:
            result = session.query(
                ProgramSemester.id,
                ProgramSemester.uid,
                ProgramSemester.program_code,
                ProgramSemester.created_at,
                ProgramSemester.updated_at,
                ProgramSemester.ac_year,
                ProgramSemester.study_year,
                ProgramSemester.semester,
                ProgramSemester.core_cwt,
                ProgramSemester.opt_cwt
            ).filter(Staff.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_program_sem_units_uids(uids: List[str]) -> List[ProgramSemester]:
        """
            Get ProgramSemUnit by
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where((ProgramSemester.uid.in_(uids)) & (Staff.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_sem_units_uid(uid: str) -> List[ProgramSemester]:
        """
            Get ProgramSemUnit by
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where(ProgramSemester.uid == uid & ProgramSemester.deleted_at.is_(None))
            result = session.scalars(stmt)
            return result.all()

    def register_program_sem_units(self, inputs: List[ProgramSemester]) -> Response[List[ProgramSemesterNode]]:
        """
        Register ProgramSemUnit
        :param inputs:
        :return:
        """
        program_semester_list = []
        with session_scope() as session:
            # Check if program semester already exist using uid
            existed_program_semester_list = self.get_program_sem_units_uids(
                [ProgramSemester.uid for program_se_unit in inputs if program_se_unit.uid is None])
            if existed_program_semester_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_program_semester_list,
                                message="program semester unit Already Exists")
            # check for existing Users using uid
            existed_program_semester = self.get_program_sem_units_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    program_semester = ProgramSemester(
                        program_code=ProgramSemester.program_code,
                        ac_year=ProgramSemester.ac_year,
                        study_year=ProgramSemester.study_year,
                        semester=ProgramSemester.semester,
                        core_cwt=ProgramSemester.core_cwt,
                        opt_cwt=ProgramSemester.opt_cwt,
                        created_by=ProgramSemester.created_by
                    )
                    program_semester_list.append(program_semester)
                else:
                    program_semester = next(filter(lambda staff: str(staff.uid) == str(inputItem.uid),
                                                   existed_program_semester), None)

                    if program_semester:
                        program_semester.uid = inputItem.uid
                        program_semester_list.append(program_semester)
            session.add_all(program_semester_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=program_semester_list,
                            message="Successfully Submitted")
