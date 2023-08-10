from typing import List, Optional

import pendulum
from sqlalchemy import select, desc
from src.db.session import session_scope
from src.models import ProgramCategory, StudentProgramChangeStatus
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentProgramChangeStatusInput


class StudentProgramChangeStatusService:
    @staticmethod
    def get_student_program_changes_status() -> List[StudentProgramChangeStatus]:
        with session_scope() as session:
            result = session.query(StudentProgramChangeStatus).filter(
                StudentProgramChangeStatus.deleted_at.is_(None)).order_by(
                desc(StudentProgramChangeStatus.updated_at)).all()
            return result

    @staticmethod
    def get_student_program_changes_status_by_uid(uid: str) -> StudentProgramChangeStatus:
        """
        Get student program change status category  by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentProgramChangeStatus).where(
                (StudentProgramChangeStatus.uid == uid) & (StudentProgramChangeStatus.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()


    @staticmethod
    def get_student_program_changes_status_by_uids(uids: List[str]) -> List[StudentProgramChangeStatus]:
        """
        Get many student programs change status by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentProgramChangeStatus).where(
                (StudentProgramChangeStatus.uid.in_(uids)) & (StudentProgramChangeStatus.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_student_program_changes_status_by_names(names: List[str]) -> List[ProgramCategory]:
        """
        Get student program change
        :param names:
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentProgramChangeStatus).where(
                (StudentProgramChangeStatus.name.in_(names)) & (StudentProgramChangeStatus.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    def register_student_program_change_status(self, inputs: List[StudentProgramChangeStatusInput]) -> Response[List[Optional[StudentProgramChangeStatus]]]:
        """
        Register student programs change status
        :param inputs:
        :return Response[List[Optional[StudentProgramChangeStatus]]]
        """
        program_change_status_list = []
        action_type = "Register"
        with session_scope() as session:
            # Check if the program change category already exist using uid
            existed_student_program_change_status_list = self.get_student_program_changes_status_by_names(
                [student_program_change_status.code for student_program_change_status in inputs if student_program_change_status.name is None])
            if existed_student_program_change_status_list:
                return Response(status=False, code=ResponseCode.DUPLICATE,
                                data=existed_student_program_change_status_list,
                                message="Program Change Status Already Exists")

            # check for existing programs categories using uid
            existed_program_change_status = self.get_student_program_changes_status_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    student_program_change_status = StudentProgramChangeStatus(
                        name=inputItem.name,
                        code=inputItem.code
                    )
                    program_change_status_list.append(student_program_change_status)
                else:
                    action_type = "Update"
                    student_program_change = next(
                        filter(lambda program_change_status: str(program_change_status.uid) == str(inputItem.uid),
                               existed_student_program_change_status_list), None)

                    if student_program_change:
                        student_program_change.code = inputItem.code
                        student_program_change.name = inputItem.name
                        program_change_status_list.append(student_program_change)
            session.add_all(program_change_status_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=program_change_status_list,
                            message=f"Successfully to {action_type} Student Program Change")

    # Delete FUnction
    @staticmethod
    def remove_student_program_change(uid: str):
        """
        Remove Program Category by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(StudentProgramChangeStatus).filter_by(uid=uid).update({StudentProgramChangeStatus.deleted_at: pendulum.now()})
            session.commit()
