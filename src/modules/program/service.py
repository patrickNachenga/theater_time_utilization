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
        with session_scope() as session:
            result = session.query(
                Program.id,
                Program.uid,
                Program.code,
                Program.name,
                Program.short_name,
                Program.max_student,
                Program.tcu_code,
                Program.program_number,
                Program.program_type_id,
                Program.created_by,
                Program.specialization_area_id,
                Program.institute_unit_id,
                Program.qualification,
                Program.action,
                Program.created_at,
                Program.updated_at,
            ).filter(Program.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_program_by_program_numbers(program_numbers: List[str]) -> List[Program]:
        """
            Get program by program_number
        :return:
        """
        with session_scope() as session:
            stmt = select(Program).where(
                (Program.program_number.in_(program_numbers)) & (Program.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_by_uids(uids: List[str]) -> List[Program]:
        """
            Get programs by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(Program).where((Program.uid.in_(uids)) & (Program.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_by_program_number(program_number: str) -> Program:
        """
        Get Program by program_numbers
        :param:
        :return:
        """
        with session_scope() as session:
            stmt = select(Program).where(
                (Program.program_number == program_number) & (Program.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_get_program(self, inputs: List[ProgramInput]) -> Response[List[ProgramNode]]:
        """
        Register Program
        :param inputs:
        :return:
        """
        program_list = []
        with session_scope() as session:
            # Check if program already exist using program_number
            existed_program_list = self.get_program_by_program_numbers(
                [Program.program_number for program in inputs if program.uid is None])
            if existed_program_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_program_list,
                                message="Program Already Exists")
            # check for existing Program using uid
            existed_program = self.get_program_by_uids([item.uid for item in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    program = Program(
                        program_number=inputItem.program_number,
                        code=inputItem.code,
                        name=inputItem.name,
                        short_name=inputItem.short_name,
                        tcu_code=inputItem.tcu_code,
                        duration=inputItem.duration,
                        qualification=inputItem.qualification,
                        max_student=inputItem.max_student,
                        action=inputItem.action,
                        created_by=inputItem.created_by,
                        program_type_id=inputItem.program_type_id,
                        specialization_area_id=inputItem.specialization_area_id,
                        institute_unit_id=inputItem.institute_unit_id,
                    )
                    program_list.append(program)
                else:
                    program = next(filter(lambda program: str(program.uid) == str(inputItem.uid),
                                            existed_program), None)

                    if program:
                        program.program_number = inputItem.program_number,
                        program.code = inputItem.code,
                        program.name = inputItem.name,
                        program.short_name = inputItem.short_name,
                        program.tcu_code = inputItem.tcu_code,
                        program.duration = inputItem.duration,
                        program.qualification = inputItem.qualification,
                        program.max_student = inputItem.max_student,
                        program.action = inputItem.action,
                        program.created_by = inputItem.created_by,
                        program.program_type_id = inputItem.program_type_id,
                        program.specialization_area_id = inputItem.specialization_area_id,
                        program.institute_unit_id = inputItem.institute_unit_id,
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
