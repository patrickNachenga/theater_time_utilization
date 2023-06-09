from typing import List

import pendulum

from src.db.session import session_scope
from src.models import ProgramCapacity, AcademicYear
from src.models.program import Program
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCapacityInputNode, ProgramCapacityListNode


class ProgramCapacityService:
    @staticmethod
    def get_program_capacity(program_uid: str) -> List[ProgramCapacity]:
        """
            Get all program capacity by program id
        :return:
        """
        with session_scope() as session:
            program = session.query(Program).filter(Program.uid == program_uid).first()
            result = session.query(ProgramCapacity).filter(ProgramCapacity.program_id == program.id).order_by(
                ProgramCapacity.id.desc()).all()
            return result

    def register_program_capacity(self, inputs: ProgramCapacityInputNode) -> Response[ProgramCapacityListNode]:
        """
           Register Program capacity
           :param inputs:
           :return:
           """

        with session_scope() as session:
            program = session.query(Program).filter(Program.uid == inputs.program_uid).first()
            academic_year = session.query(AcademicYear).filter(AcademicYear.uid == inputs.academic_year_uid).first()

            if inputs.uid:
                program_capacity = session.query(ProgramCapacity).filter(ProgramCapacity.uid == inputs.uid).first()

                if program_capacity is None:
                    return Response(status=True, code=ResponseCode.NO_RECORD_FOUND, data=[],
                                    message=f"Program capacity not found")

                program_capacity.program = program
                program_capacity.academic_year = academic_year
                program_capacity.is_active = inputs.is_active
            else:
                program_capacity = ProgramCapacity(
                    program=program,
                    academic_year=academic_year,
                    is_active=inputs.is_active
                )

            session.add(program_capacity)
            session.commit()

            all_program_capacities = session.query(ProgramCapacity).order_by(ProgramCapacity.id.desc()).all()
            count = len(all_program_capacities)

            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                data=ProgramCapacityListNode(items=all_program_capacities, total_count=count),
                message="Successfully saved program capacity"
            )

    @staticmethod
    def remove_program_capacity(uid: str):
        """
            Remove Program by UID
            :param uid:
            :return:
            """
        with session_scope() as session:
            program_capacity = session.query(ProgramCapacity).filter(ProgramCapacity.uid == uid,
                                                                     ProgramCapacity.is_active == True).first()
            if program_capacity is None:
                return Response(status=True, code=ResponseCode.FAILURE, data=[], message=f"Program capacity not found")

            if program_capacity.is_active:
                return Response(status=True, code=ResponseCode.FAILURE, data=[],
                                message=f"Cannot remove active program capacity")

            program_capacity.deleted_at = pendulum.now()
            all_program_capacities = session.query(ProgramCapacity).filter(ProgramCapacity.is_active == True).order_by(
                ProgramCapacity.id.desc()).all()
            count = len(all_program_capacities)
            session.commit()

        return Response(status=True, code=ResponseCode.SUCCESS, data=[],
                        message="Program capacity removed successfully")
