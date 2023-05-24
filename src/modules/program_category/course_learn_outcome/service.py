from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models.program import Program
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramInput, ProgramNode


class ProgramService(object):
    @staticmethod
    def get_programs() -> List[Program]:
        """
            Get all programs by program
        :return:
        """
        with session_scope() as session:
            result = session.query(
                Program.id,
                Program.uid,
                Program.code,
                Program.name,
                Program.short_name,
                Program.tcu_code,
                Program.reg_code,
                Program.nacte_code,
                Program.program_category_id,
                Program.department_id,
                Program.campus_id,
                Program.duration,
            ).filter(Program.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_program_by_ids(ids: List[str]) -> List[Program]:
        """
            Get programs by program ids
        :param:ids
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

    def register_program(self, inputs: List[ProgramInput]) -> Response[List[ProgramNode]]:
        """
        Register Program
        :param inputs:
        :return:
        """
        program_list = []
        with session_scope() as session:
            # Check if student already exist using reg_no
            existed_program_list = self.get_program_by_codes(
                [program.code for program in inputs if program.uid is None])
            if existed_program_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_program_list,
                                message="Program Already Exists")

            # check for existing Program using uid
            existed_program = self.get_program_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    program = Program(
                        code=inputItem.code,
                        name=inputItem.name,
                        short_name=inputItem.short_name,
                        tcu_code=inputItem.tcu_code,
                        reg_code=inputItem.reg_code,
                        nacte_code=inputItem.nacte_code,
                        program_category_id=inputItem.program_category_id,
                        department_id=inputItem.department_id,
                        campus_id=inputItem.campus_id,
                        duration=inputItem.duration,
                    )

                    program_list.append(program)
                else:
                    program = next(filter(lambda program: str(program.uid) == str(inputItem.uid),
                                          existed_program), None)
                    if program:
                        program.code = inputItem.code,
                        program.name = inputItem.name,
                        program.short_name = inputItem.short_name,
                        program.tcu_code = inputItem.tcu_code,
                        program.reg_code = inputItem.reg_code,
                        program.nacte_code = inputItem.nacte_code,
                        program.program_category_id = inputItem.program_category_id,
                        program.department_id = inputItem.department_id,
                        program.campus_id = inputItem.campus_id,
                        program.duration = inputItem.duration,
                        program_list.append(program)
            session.add_all(program_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=program_list,
                            message="Successfully Submitted")

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
