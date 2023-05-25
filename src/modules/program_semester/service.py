from typing import List

import pendulum
from sqlalchemy import select
from src.db.session import session_scope
from src.models.program_semester import ProgramSemester
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramSemesterInput, ProgramSemesterNode


class ProgramSemesterService(object):
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

    def register_program_semesters(self, inputs: List[ProgramSemesterInput]) -> Response[List[ProgramSemesterNode]]:
        """
        Register programs semesters
        :param inputs:
        :return:
        """
        program_semester_list = []
        action_type = "Register"
        print("---------------------------------------------------------------")
        with session_scope() as session:
            # Check if the programs category already exist using uid
            existed_program_semester_list = self.get_program_semester_by_uids(
                [program_semester.uid for program_semester in inputs if program_semester.uid is None])
            if existed_program_semester_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_program_semester_list,
                                message="Program Category Already Exists")
            # check for existing programs semesters using uid
            existed_program_semester = self.get_program_semester_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    program_semester = ProgramSemester(
                        study_year=inputItem.study_year,
                        semester=inputItem.semester,
                        created_by=inputItem.created_by,
                        program_id=inputItem.program_id,
                        academic_year_id=inputItem.academic_year_id,
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
                        program_semester.program_id = inputItem.program_id
                        program_semester.academic_year_id = inputItem.academic_year_id
                        program_semester.core_credits = inputItem.core_credits
                        program_semester.elective_credits = inputItem.elective_credits
                        program_semester_list.append(program_semester)
            session.add_all(program_semester_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=program_semester_list,
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
