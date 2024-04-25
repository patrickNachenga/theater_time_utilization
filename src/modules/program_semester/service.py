from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc

from src.core.security import Info
from src.db.session import session_scope
from src.helpers.utils import get_user_departments_headship, get_user_unit_department_headship
from src.models import Program, AcademicYear, ProgramCourse
from src.models.program_semester import ProgramSemester
from src.modules import CRUDBase
from src.modules.academic_year.service import AcademicYearService
from src.modules.programs.service import ProgramService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramSemesterInput, ProgramSemesterListNode, InnerStudentProgramSemester, \
    ProgramSemesterForwardStatus


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
    def get_program_semester_by_data(semester, year_of_study, program_id, academic_year_id) -> ProgramSemester:
        """
        Get program semester by uid
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramSemester).where(
                ProgramSemester.semester == semester, ProgramSemester.study_year == year_of_study,
                ProgramSemester.program_id == program_id,
                ProgramSemester.academic_year_id == academic_year_id and (ProgramSemester.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_hod_program_semester(academic_year_uid, semester, info: Info) -> List[ProgramSemester]:
        with session_scope() as session:
            # print(academic_year_uid)
            academic_year = AcademicYearService.get_academic_year_by_uid(academic_year_uid)
            if academic_year is None:
                return []
            user_h_department_uids = get_user_departments_headship(info)
            programs = session.query(ProgramSemester).join(Program).filter(
                ProgramSemester.academic_year_id == academic_year.id,
                ProgramSemester.deleted_at.is_(None),
                ProgramSemester.semester == semester,
                Program.department_uid.in_(user_h_department_uids),
                Program.deleted_at.is_(None)).order_by(Program.name.asc(), ProgramSemester.study_year.asc()).all()
            return programs

    @staticmethod
    def get_program_semester_forward_status(academic_year_uid, semester, forward_status, info: Info) \
            -> Response[List[ProgramSemesterForwardStatus]]:
        with session_scope() as session:
            # print(academic_year_uid)
            academic_year = AcademicYearService.get_academic_year_by_uid(academic_year_uid)
            if academic_year is None:
                return Response(
                    status=False,
                    code=ResponseCode.NO_RECORD_FOUND,
                    message="Academic Year is not registered",
                    data=None)
            new_forward_status = forward_status + 1
            programs = []
            return_program_data = []
            if forward_status == 2:
                user_h_department_uids = get_user_unit_department_headship(info)
                program_semesters = session.query(ProgramSemester).join(Program).filter(
                    ProgramSemester.academic_year_id == academic_year.id,
                    ProgramSemester.deleted_at.is_(None),
                    ProgramSemester.semester == semester,
                    Program.department_uid.in_(user_h_department_uids),
                    Program.deleted_at.is_(None)).order_by(Program.name.asc(), ProgramSemester.study_year.asc()).all()

                if program_semesters:
                    for ps in program_semesters:
                        all_program_courses = session.query(ProgramCourse) \
                            .filter(
                            ProgramCourse.deleted_at.is_(None),
                            ProgramCourse.program_semester_id == ps.id).count()

                        total_forwarded_status = session.query(ProgramCourse).filter(
                            ProgramCourse.deleted_at.is_(None), ProgramCourse.program_semester_id == ps.id,
                                                                ProgramCourse.forward_status >= new_forward_status).count()
                        return_program_data.append(ProgramSemesterForwardStatus(
                            program_semester_uid=ps.uid,
                            program_name=ps.program.name,
                            program_code=ps.program.code,
                            study_year=ps.study_year,
                            forward_status=True if total_forwarded_status == all_program_courses else False,
                            remark=f"{total_forwarded_status} out of {all_program_courses}"
                        ))

                    return Response(
                        status=False,
                        code=ResponseCode.SUCCESS,
                        message="Program Semester Retrieved Successfully",
                        data=return_program_data)
                    # print(return_program_data)
            if forward_status == 3:
                program_semesters = session.query(ProgramSemester).join(Program).filter(
                    ProgramSemester.academic_year_id == academic_year.id,
                    ProgramSemester.deleted_at.is_(None),
                    ProgramSemester.semester == semester,
                    Program.deleted_at.is_(None)).order_by(Program.name.asc(), ProgramSemester.study_year.asc()).all()

                if program_semesters:
                    for ps in program_semesters:
                        all_program_courses = session.query(ProgramCourse) \
                            .filter(
                            ProgramCourse.deleted_at.is_(None),
                            ProgramCourse.program_semester_id == ps.id).count()

                        total_forwarded_status = session.query(ProgramCourse).filter(
                            ProgramCourse.deleted_at.is_(None), ProgramCourse.program_semester_id == ps.id,
                                                                ProgramCourse.forward_status >= new_forward_status).count()
                        return_program_data.append(ProgramSemesterForwardStatus(
                            program_semester_uid=ps.uid,
                            program_name=ps.program.name,
                            program_code=ps.program.code,
                            study_year=ps.study_year,
                            forward_status=True if total_forwarded_status == all_program_courses else False,
                            remark=f"{total_forwarded_status} out of {all_program_courses}"
                        ))

                    return Response(
                        status=False,
                        code=ResponseCode.SUCCESS,
                        message="Program Semester Retrieved Successfully",
                        data=return_program_data)
                    # print(return_program_data)

            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="No Program Semester Record Found",
                data=None)
            # return programs

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
