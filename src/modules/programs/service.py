from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models.program import Program
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramInput, ProgramListNode


class ProgramService(CRUDBase[Program, ProgramInput, ProgramInput]):
    @staticmethod
    def get_programs() -> List[Program]:
        """
            Get all programs by program
        :return:
        """
        with session_scope() as session:
            result = session.query(Program).filter(Program.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_program_by_ids(ids: List[str]) -> List[Program]:
        """
            Get programs by program ids
        :param ids:
        :return:List[Program]
        """
        with session_scope() as session:
            stmt = select(Program).where(
                (Program.id.in_(ids)) & (Program.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_by_uids(uids: List[str]) -> List[Program]:
        """
            Get programs by uids
        :param:uids
        :return:List[Program]
        """
        with session_scope() as session:
            stmt = select(Program).where((Program.uid.in_(uids)) & (Program.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_by_codes(codes: List[str]) -> List[Program]:
        """
            Get programs by codes
        :param:codes
        :return:List[Program]
        """
        with session_scope() as session:
            stmt = select(Program).where((Program.code.in_(codes)) & (Program.deleted_at.is_(None)))
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
    def get_program_by_id(id: str) -> Program:
        """
        Get Program by id
        :param:id
        :return:Program
        """
        with session_scope() as session:
            stmt = select(Program).where(
                (Program.id == id) & (Program.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

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
            existed_program_list = self.get_program_by_codes(
                [program.code for program in inputs if program.uid is None])
            if existed_program_list:
                return Response(status=False, code=ResponseCode.DUPLICATE,
                                data=ProgramListNode(items=existed_program_list, total_count=0),
                                message="Program  Already Exists")

            # check for existing Program using uid
            existed_program = self.get_program_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    program = Program(
                        code=inputItem.code,
                        name=inputItem.name,
                        short_name=inputItem.short_name,
                        tcu_code=inputItem.tcu_code,
                        registration_code=inputItem.registration_code,
                        nacte_code=inputItem.nacte_code,
                        program_category_id=inputItem.program_category_id,
                        department_uid=inputItem.department_uid,
                        duration=inputItem.duration,
                    )

                    program_list.append(program)
                else:
                    action_type = "Update"
                    program = next(filter(lambda program: str(program.uid) == str(inputItem.uid),
                                          existed_program), None)
                    if program:
                        program.code = inputItem.code,
                        program.name = inputItem.name,
                        program.short_name = inputItem.short_name,
                        program.tcu_code = inputItem.tcu_code,
                        program.registration_code = inputItem.registration_code,
                        program.nacte_code = inputItem.nacte_code,
                        program.program_category_id = inputItem.program_category_id,
                        program.department_uid = inputItem.department_uid,
                        program.duration = inputItem.duration,
                        program_list.append(program)
            session.add_all(program_list)
            count = session.query(Program).filter(Program.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=ProgramListNode(items=program_list, total_count=count),
                            message=f"Successfully to {action_type} Program category")

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
    async def api_get_program_by_code(code: str) -> Response:
        """
            Get programs by codes
        :param code:
        """
        try:
            program = ProgramService.get_program_by_code(code)
            print(program.uid)
            return Response(status=True, code=ResponseCode.SUCCESS, data={
                "uid": program.uid,
                "code": program.code,
                "name": program.name,
                "short_name": program.short_name,
            }, message="Program retrieved Successfully")
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE,
                            message=f"fail to find program with code : {code}", data={})


ProgramCrud = ProgramService(Program)
