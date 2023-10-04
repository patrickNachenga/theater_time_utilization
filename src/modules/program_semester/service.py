from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc

from src.db.session import session_scope
from src.models import Program, AcademicYear
from src.models.program_semester import ProgramSemester
from src.modules import CRUDBase
from src.modules.academic_year.service import AcademicYearService
from src.modules.programs.service import ProgramService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramSemesterInput, ProgramSemesterListNode, InnerStudentProgramSemester


class ProgramSemesterService(CRUDBase[ProgramSemester, ProgramSemesterInput, ProgramSemesterInput]):
    @staticmethod
    def get_program_semesters() -> List[ProgramSemester]:
        with session_scope() as session:
            result = session.query(ProgramSemester).filter(ProgramSemester.deleted_at.is_(None)).order_by(
                desc(ProgramSemester.updated_at)).all()
            return result


    @staticmethod
    def get_program_semesters_by_ids(ids: List[str]) -> List[ProgramSemester]:
        """
        Get programs semesters by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where(
                (ProgramSemester.id.in_(ids)) & (ProgramSemester.deleted_at.is_(None))).order_by(
                desc(ProgramSemester.updated_at))
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
    def get_program_semester_by_program_id(program_id: int) -> ProgramSemester:
        """
        Get program semester by program_id
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where(
                (ProgramSemester.program_id == program_id) & (ProgramSemester.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_program_semester_by_program_uid(program_uid: str) -> ProgramSemester:
        """
        Get program semester by program_uid
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where(
                (ProgramSemester.programs.uid == program_uid) & (ProgramSemester.deleted_at.is_(None)))
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

    @staticmethod
    def get_student_semester(input: InnerStudentProgramSemester) -> ProgramSemester:
        """
        Get programs semester
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where(
                (ProgramSemester.program_id.is_(input.program_id)) & (
                    ProgramSemester.academic_year_id.is_(input.academic_year_id)) &
                (ProgramSemester.study_year.is_(input.study_year)) & (ProgramSemester.semester.is_(input.semester)) &
                (ProgramSemester.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def check_uniqueness(academic_year_id: int, program_id: int, study_year: int, semester: int) -> ProgramSemester:
        """
        Check if there already exists program semester with same academicYearId, programId, studyYear, semester all together
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where(
                (ProgramSemester.academic_year_id == academic_year_id) &
                (ProgramSemester.program_id == program_id) &
                (ProgramSemester.study_year == study_year) &
                (ProgramSemester.semester == semester) &
                (ProgramSemester.deleted_at.is_(None))
            )
            result = session.scalars(stmt)
            return result.first()

    def register_program_semesters(self, inputs: List[ProgramSemesterInput]) -> Response[ProgramSemesterListNode]:
        """
        Register programs semesters
        :param inputs:
        :return:
        """
        program_semester_list = []
        action_type = "Register"

        with session_scope() as session:
            # check for existing programs semesters using uid
            existed_program_semester = self.get_program_semester_by_uids([inputItem.uid for inputItem in inputs])

            for inputItem in inputs:
                # Verify and get supplied Program uid and get existed program model
                try:
                    program = ProgramService(Program).get(inputItem.program_uid)
                    if program is None:
                        raise ValueError("You have submitted incorrect program details")
                except Exception as e:
                    print(e)
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=ProgramSemesterListNode(items=[], total_count=0),
                        message="You have submitted incorrect program details"
                    )

                # Verify and get supplied Academic year uid and get existed Academic year model
                try:
                    academic_year = AcademicYearService(AcademicYear).get(inputItem.academic_year_uid)
                    if academic_year is None:
                        raise ValueError("You submitted incorrect academic year details")
                except Exception as e:
                    print(e)
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=ProgramSemesterListNode(items=[], total_count=0),
                        message="You submitted incorrect academic year details"
                    )

                if inputItem.uid is None:
                    # validate if this program semester is not deprecated
                    deprecated_program_semester = self.check_uniqueness(academic_year_id=academic_year.id,
                                                                        program_id=program.id,
                                                                        semester=inputItem.semester,
                                                                        study_year=inputItem.study_year)
                    if deprecated_program_semester:
                        return Response(
                            status=False,
                            code=ResponseCode.FAILURE,
                            data=ProgramSemesterListNode(items=[], total_count=0),
                            message="Program Semester Already Exist"
                        )

                    program_semester = ProgramSemester(
                        study_year=inputItem.study_year,
                        semester=inputItem.semester,
                        program=program,
                        academic_year=academic_year,
                        core_credits=inputItem.core_credits,
                        elective_credits=inputItem.elective_credits
                    )
                    local_object = session.merge(program_semester)
                    session.add(local_object)
                    session.commit()
                    program_semester_list.append(local_object)
                else:
                    action_type = "Update"
                    program_semester = next(
                        filter(lambda prog_semester: str(prog_semester.uid) == str(inputItem.uid),
                               existed_program_semester), None)

                    if program_semester:

                        obj_data = jsonable_encoder(inputItem)
                        # Replace referenced uids field with model required ids field
                        obj_data['academic_year'] = academic_year
                        obj_data['program'] = program
                        for key, value in obj_data.items():
                            setattr(program_semester, key, value)

                        local_object = session.merge(program_semester)
                        session.add(local_object)
                        session.commit()
                        program_semester_list.append(local_object)

            count = session.query(ProgramSemester).filter(ProgramSemester.deleted_at.is_(None)).count()

            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=ProgramSemesterListNode(items=program_semester_list, total_count=count),
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
