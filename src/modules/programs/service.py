from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc

from src.core.moodle_api import MoodleApi
from src.db.session import session_scope
from src.models import AcademicYear
from src.models.program import Program
from src.modules import CRUDBase
from src.modules.academic_year.service import AcademicYearService
from src.modules.program_category.service import ProgramCategoryService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramInput, ProgramListNode, ProgramCodeInput


class ProgramService(CRUDBase[Program, ProgramInput, ProgramInput]):
    @staticmethod
    def get_programs() -> List[Program]:
        """
            Get all programs by program
        :return:
        """
        with session_scope() as session:
            result = session.query(Program).filter(Program.deleted_at.is_(None)).order_by(
                desc(Program.updated_at)).all()
            return result

    @staticmethod
    def get_program_by_uids(uids: List[str]) -> List[Program]:
        """
            Get programs by uids
        :param:uids
        :return:List[Program]
        """
        with session_scope() as session:
            stmt = select(Program).where((Program.uid.in_(uids)) & (Program.deleted_at.is_(None))).order_by(
                desc(Program.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_ids_by_uids(uids: List[str]) -> List:
        """
            Get programs_uid by uids
        :param:uids
        :return:List[str]
        """
        with session_scope() as session:
            stmt = select(Program.id, Program.uid).where(
                (Program.uid.in_(uids)) & (Program.deleted_at.is_(None))).order_by(
                desc(Program.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def api_get_program_by_departments(uids: List[str]) -> List[str]:
        """
            Get programs by department_uids
        :param:uids
        :return:List[Program]
        """
        with session_scope() as session:
            stmt = select(Program.uid).where(
                (Program.department_uid.in_(uids)) & (Program.deleted_at.is_(None))).order_by(
                desc(Program.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_programs_by_category(category_uid: str) -> Response[ProgramListNode]:
        """
            Get programs by program category uids
        :param:category_uid
        :return:List[ProgramListNode]
        """
        with session_scope() as session:
            # Verify and get supplied program uid. and get existed year id from returned Program model
            try:
                program_category_id = ProgramCategoryService.get_program_category_by_uid(category_uid).id
            except Exception as e:
                print(e)
                return Response(status=False, code=ResponseCode.FAILURE,
                                data=ProgramListNode(items=[], total_count=0),
                                message="You have submitted incorrect program category details")

            stmt = select(Program).where(
                (Program.program_category_id == program_category_id) & (Program.deleted_at.is_(None))).order_by(
                desc(Program.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_programs_by_department(department_uid: str) -> Response[ProgramListNode]:
        """
            Get programs by department uids
        :param department_uid:
        :return List[ProgramListNode]:
        """
        with session_scope() as session:
            stmt = select(Program).where(
                (Program.department_uid == department_uid) & (Program.deleted_at.is_(None))).order_by(
                desc(Program.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_by_uid(uid: str) -> Program:
        """
        Get Program by uid
        :param uid:
        :return:Program
        """
        with session_scope() as session:
            stmt = select(Program).where(
                (Program.uid == uid) & (Program.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_program_by_codes(codes: List[str]) -> List[Program]:
        """
            Get programs by codes
        :param:codes
        :return:List[Program]
        """
        with session_scope() as session:
            stmt = select(Program).where((Program.code.in_(codes)) & (Program.deleted_at.is_(None))).order_by(
                desc(Program.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_by_code(code: str) -> Program:
        """
        Get Program by code
        :param:
        :return:Program
        """
        with session_scope() as session:
            stmt = select(Program).where(
                (Program.code == code) & (Program.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_program_by_names(names: List[str]) -> List[Program]:
        """
            Get programs by names
        :param names:
        :return:List[Program]
        """
        with session_scope() as session:
            stmt = select(Program).where((Program.name.in_(names)) & (Program.deleted_at.is_(None))).order_by(
                desc(Program.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_by_name(name: str) -> Program:
        """
        Get Program by name
        :param name:
        :return:Program
        """
        with session_scope() as session:
            stmt = select(Program).where(
                (Program.name == name) & (Program.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    # @staticmethod
    # def get_program_by_code(code: str) -> Program:
    #     """
    #     Get Program by name
    #     :param code:
    #     :return:Program
    #     """
    #     with session_scope() as session:
    #         stmt = select(Program).where(
    #             (Program.code == code) & (Program.deleted_at.is_(None)))
    #         result = session.scalars(stmt)
    #         return result.first()

    def register_program(self, inputs: List[ProgramInput]) -> Response[ProgramListNode]:
        """
        Register Program
        :param inputs:
        :return:
        """
        program_list = []
        action_type = "Register"
        with session_scope() as session:
            # Check if program already exist using code
            existed_program_code_list = self.get_program_by_codes(
                [program.code for program in inputs if program.uid is None])
            # Check if program already exist using name
            existed_program_name_list = self.get_program_by_names(
                [program.name for program in inputs if program.uid is None])
            if existed_program_code_list or existed_program_name_list:
                return Response(status=False, code=ResponseCode.DUPLICATE,
                                data=ProgramListNode(
                                    items=existed_program_code_list if existed_program_code_list is not None else existed_program_name_list,
                                    total_count=0),
                                message="Program  Already Exists")

            # check for existing Program using uid
            existed_program = self.get_program_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                # Verify and get supplied program category uid. and get existed year id from returned Program Category model
                try:
                    program_category = ProgramCategoryService.get_program_category_by_uid(
                        inputItem.program_category_uid)
                    if program_category is None:
                        raise ValueError("You have submitted incorrect programs category details")
                except Exception as e:
                    print(e)
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    data=ProgramListNode(items=[], total_count=0),
                                    message="You have submitted incorrect program category details")

                if inputItem.uid is None:
                    program = Program(
                        code=inputItem.code,
                        name=inputItem.name,
                        short_name=inputItem.short_name,
                        tcu_code=inputItem.tcu_code,
                        registration_code=inputItem.registration_code,
                        nacte_code=inputItem.nacte_code,
                        program_category=program_category,
                        department_uid=inputItem.department_uid,
                        duration=inputItem.duration,
                    )
                    session.add(program)
                    session.commit()
                    program_list.append(program)
                else:
                    action_type = "Update"
                    program = next(filter(lambda program: str(program.uid) == str(inputItem.uid),
                                          existed_program), None)
                    if program:
                        obj_data = jsonable_encoder(inputItem)
                        # Replace referenced uids field with model required ids field
                        obj_data['program_category_id'] = program_category.id
                        for key, value in obj_data.items():
                            setattr(program, key, value)

                        session.add(program)
                        session.commit()
                        program_list.append(program)
            count = session.query(Program).filter(Program.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=ProgramListNode(items=program_list, total_count=count),
                            message=f"Successfully to {action_type} Program")

    @staticmethod
    def remove_program(uid: str):
        """
        Remove Program by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(Program).filter_by(uid=uid).update({Program.deleted_at: pendulum.now()})
            session.commit()

    @staticmethod
    async def api_get_program_by(code: str | None = None, uid: str | None = None) -> Response:
        """
            Get programs by codes
        :param:
        """
        try:
            if code:
                program = ProgramService.get_program_by_code(code)
            elif uid:
                program = ProgramService.get_program_by_uid(uid)

            # academic_year:AcademicYear
            academic_year = AcademicYearService.get_active_academic_year()

            return Response(status=True, code=ResponseCode.SUCCESS, data={
                "uid": program.uid,
                "code": program.code,
                "name": program.name,
                "short_name": program.short_name,
                "duration":program.duration,
                "department_uid": program.department_uid,
                "program_category_name": program.program_category.name,
                "program_category_short_name": program.program_category.short_name,
                "active_academic_year": academic_year.name,
                "active_academic_year_uid": academic_year.uid

            }, message="Program retrieved Successfully")
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE,
                            message=f"fail to find program", data={})

    @staticmethod
    async def api_get_programs() -> Response:
        """
            Get all programs
        :param:
        """
        try:
            program = ProgramService(Program).get_programs()
            if program:
                return Response(status=True, code=ResponseCode.SUCCESS, data=[{
                    "uid": programItems.uid,
                    "code": programItems.code,
                    "name": programItems.name,
                    "short_name": programItems.short_name,
                    "department_uid": programItems.department_uid,
                    "duration": programItems.duration,
                    "program_category_name": programItems.program_category.name,
                    "program_category_short_name": programItems.program_category.short_name,
                } for programItems in program],
                                message="Program retrieved Successfully")
            else:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND, data=[],
                                message="No program found")
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE,
                            message=f"Unable to find programs", data=None)


ProgramCrud = ProgramService(Program)
