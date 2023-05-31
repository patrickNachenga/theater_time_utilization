from typing import List

import pendulum
from sqlalchemy import select
from src.db.session import session_scope
from src.models import Program, AcademicYear
from src.models.program_semester import ProgramSemester
from src.modules import CRUDBase
from src.modules.academic_year.service import AcademicYearService
from src.modules.programs.service import ProgramService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramSemesterInput, ProgramSemesterListNode


class ProgramSemesterService(CRUDBase[ProgramSemester, ProgramSemesterInput, ProgramSemesterInput]):
    @staticmethod
    def get_program_semesters() -> List[ProgramSemester]:
        with session_scope() as session:
            result = session.query(ProgramSemester).filter(ProgramSemester.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_program_semesters_by_ids(ids: List[str]) -> List[ProgramSemester]:
        """
        Get programs semesters by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where((ProgramSemester.id.in_(ids)) & (ProgramSemester.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_semester_by_uid(uid: str) -> ProgramSemester:
        """
        Get program semester by uid
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where(
                (ProgramSemester.uid == uid) & (ProgramSemester.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()


    @staticmethod
    def get_program_semester_by_uids(uids: List[str]) -> List[ProgramSemester]:
        """
        Get programs category by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where(
                (ProgramSemester.uid.in_(uids)) & (ProgramSemester.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    def register_program_semesters(self, inputs: List[ProgramSemesterInput]) -> Response[ProgramSemesterListNode]:
        """
        Register programs semesters
        :param inputs:
        :return:
        """
        program_semester_list = []
        existed_program: List[Program]
        academic_year: List[AcademicYear]
        action_type = "Register"
        with session_scope() as session:
            # check for existing programs semesters using uid
            existed_program_semester = self.get_program_semester_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                # Verify and get supplied Program uid. and get existed program id from returned program model
                try:
                    program_id = ProgramService.get_program_by_uid(inputItem.program_uid).id
                except Exception as e:
                    print(e)
                    return Response(status=False, code=ResponseCode.FAILURE, data=ProgramSemesterListNode(items=[], total_count=0),
                                    message="Please make sure you have submitted correct program value")

                # Verify and get supplied Academic year uid. and get existed Academic year id from returned Academic year model
                try:
                    academic_year_id = AcademicYearService.get_academic_year_by_uid(inputItem.academic_year_uid).id
                except Exception as e:
                    print(e)
                    return Response(status=False, code=ResponseCode.FAILURE, data=ProgramSemesterListNode(items=[], total_count=0),
                                    message="Please make sure you submitted correct academic year value")

                if inputItem.uid is None:
                    program_semester = ProgramSemester(
                        study_year=inputItem.study_year,
                        semester=inputItem.semester,
                        program_id=program_id,
                        academic_year_id=academic_year_id,
                        core_credits=inputItem.core_credits,
                        elective_credits=inputItem.elective_credits
                    )
                    program_semester_list.append(program_semester)
                else:
                    action_type = "Update"
                    program_semester = next(
                        filter(lambda program_semester: str(program_semester.uid) == str(inputItem.uid),
                               existed_program_semester), None)

                    if program_semester:
                        program_semester.study_year = inputItem.study_year
                        program_semester.semester = inputItem.semester
                        program_semester.created_by = inputItem.created_by
                        program_semester.program_id = program_id
                        program_semester.academic_year_id = academic_year_id
                        program_semester.core_credits = inputItem.core_credits
                        program_semester.elective_credits = inputItem.elective_credits
                        program_semester_list.append(program_semester)
            session.add_all(program_semester_list)
            count = session.query(ProgramSemester).filter(ProgramSemester.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,  data=ProgramSemesterListNode(items=program_semester_list, total_count=count),
                            message=f"Successfully to {action_type} Program Semester")

    # Delete FUnction
    @staticmethod
    def remove_program_semester(uid: str):
        """
        Remove Program Category by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(ProgramSemester).filter_by(uid=uid).update({ProgramSemester.deleted_at: pendulum.now()})
            session.commit()


ProgramSemesterCrud = ProgramSemesterService(ProgramSemester)
