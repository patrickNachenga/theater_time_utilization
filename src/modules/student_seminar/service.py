from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc

from src.db.session import session_scope
from src.models.student_seminar import StudentSeminar
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentSeminarInput, StudentSeminarNode, StudentSeminarListNode


class StudentSeminarService(CRUDBase[StudentSeminar, StudentSeminarInput, StudentSeminarInput]):
    @staticmethod
    def get_student_seminar() -> List[StudentSeminar]:
        with session_scope() as session:
            result = session.query(StudentSeminar).order_by(
                desc(StudentSeminar.updated_at)).all()
            return result

    @staticmethod
    def get_student_seminar_by_names(uid: List[str]) -> List[StudentSeminar]:
        """
        Get seminar Type by names
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentSeminar).where(
                (StudentSeminar.uid.in_(uid)) & (StudentSeminar.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_student_seminar_by_uids(uids: List[str]) -> List[StudentSeminar]:
        """
        Get Seminar Types by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentSeminar).where((StudentSeminar.uid.in_(uids)) & (StudentSeminar.deleted_at.is_(None))).order_by(
                desc(StudentSeminar.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_student_seminar_by_uid(uid: str) -> StudentSeminar:
        """
        Get seminar_type by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentSeminar).where((StudentSeminar.uid == uid) & (StudentSeminar.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_student_seminar(self, inputs: List[StudentSeminarInput]) -> Response[StudentSeminarListNode]:
        """
        Register Seminar Types
        :param inputs:
        :return:
        """
        student_seminar_list = []
        action_name = "Register"
        with session_scope() as session:
            # Check if the Student Seminar already exist using uid
            existed_student_seminar_list = self.get_student_seminar_by_names(
                [student_seminar.name for student_seminar in inputs if student_seminar.uid is None])
            if existed_student_seminar_list:
                return Response(status=False, code=ResponseCode.DUPLICATE,
                                data=StudentSeminarNode(items=existed_student_seminar_list, total_count=0),
                                message="Student Seminar Already Exists")
            # check for existing seminar types using uid
            existed_student_seminar = self.get_student_seminar_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    student_seminar = StudentSeminar(
                        title=inputItem.title,
                        seminarDate=inputItem.seminarDate,
                        isPass=inputItem.isPass,
                        seminarMarks=inputItem.seminarMarks,
                        studentId=inputItem.studentId,
                        seminarTypesUid=inputItem.seminarTypesUid,
                    )
                    student_seminar_list.append(student_seminar)
                else:
                    action_name = "Update"
                    student_seminar = next(
                        filter(lambda student_seminar: str(student_seminar.uid) == str(inputItem.uid),
                               existed_student_seminar), None)
                    if student_seminar:
                        obj_data = jsonable_encoder(inputItem)
                        for key, value in obj_data.items():
                            setattr(student_seminar, key, value)
                        student_seminar_list.append(student_seminar)
            session.add_all(student_seminar_list)
            count = session.query(StudentSeminar).filter(StudentSeminar.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=StudentSeminarNode(items=student_seminar_list, total_count=count),
                            message=f"Successfully to {action_name} Student Seminar")

    # Delete Function
    @staticmethod
    def remove_student_seminar(uid: str):
        """
        Remove Student seminar by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(StudentSeminar).filter_by(uid=uid).update({StudentSeminar.deleted_at: pendulum.now()})
            session.commit()


StudentSeminarCrud = StudentSeminarService(StudentSeminar)
