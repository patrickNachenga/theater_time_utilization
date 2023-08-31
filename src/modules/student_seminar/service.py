import uuid
from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc

from src.db.session import session_scope
from src.modules.seminar_types.service import SeminarTypeService
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
    def check_uniqueness(student_uid: str, seminar_type_id: int) -> StudentSeminar:
        """
        Check if there already exists Student Seminar with same course_id, program_semester_id all together
        :return ProgramCourse:
        """
        with session_scope() as session:
            stmt = select(StudentSeminar).where(
                (StudentSeminar.seminar_type_id == seminar_type_id) &
                (StudentSeminar.student_uid == student_uid) &
                (StudentSeminar.deleted_at.is_(None))
            )
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_student_seminar_by_student_uid(inputs) -> List[StudentSeminar]:
        """
        Get Student seminar  by Student Uid
        :return:
        """
        with session_scope() as session:
            if inputs.seminar_type_uid:
                try:
                    seminar_type = SeminarTypeService.get_seminar_type_by_uid(inputs.seminar_type_uid)
                except Exception as e:
                    print(e)
                    return []
                if seminar_type is None:
                    return []
                stmt = select(StudentSeminar).where((StudentSeminar.student_uid == inputs.student_uid) & (
                    StudentSeminar.deleted_at.is_(None)) &
                                                    (StudentSeminar.seminar_type_id == seminar_type.id)
                                                    )
            else:
                stmt = select(StudentSeminar).where((
                                                            StudentSeminar.student_uid == inputs.student_uid) & (
                                                        StudentSeminar.deleted_at.is_(None)))

            result = session.scalars(stmt)
            # for seminar in result:
            #     print("Student Seminar ID:", seminar.seminar_type_id)

            return result.all()

    @staticmethod
    def get_student_seminar_by_uids(uids: List[str]) -> List[StudentSeminar]:
        """
        Get Student Seminar by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentSeminar).where(
                (StudentSeminar.uid.in_(uids)) & (StudentSeminar.deleted_at.is_(None))).order_by(
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

    def register_student_seminar(self, inputs: List[StudentSeminarInput]) -> Response[StudentSeminarNode]:
        """
        Register Seminar Types
        :param inputs:
        :return:
        """
        student_seminar_list = []
        action_name = "Register"
        with session_scope() as session:
            # Check if the Student Seminar already exist using uid
            # existed_student_seminar_list = self.get_student_seminar_by_names(
            #     [student_seminar.name for student_seminar in inputs if student_seminar.uid is None])
            # if existed_student_seminar_list:
            #     return Response(status=False, code=ResponseCode.DUPLICATE,
            #                     data=existed_student_seminar_list,
            #                     message="Student Seminar Already Exists")
            # check for existing seminar types using uid
            existed_student_seminar = self.get_student_seminar_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:

                # Verify and get supplied Seminar Type uid. and get existed Seminar Type id from returned Seminar Type model
                seminar_type = SeminarTypeService.get_seminar_type_by_uid(inputItem.seminar_types_uid)
                if seminar_type is None:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=StudentSeminarNode,
                        message="You have submitted incorrect Seminar Type details"
                    )
                print(inputItem.student_uid)
                print(seminar_type.id)
                student_seminar_exist = self.check_uniqueness(student_uid=inputItem.student_uid,
                                                              seminar_type_id=seminar_type.id)

                if inputItem.uid is None:
                    if student_seminar_exist:
                        return Response(
                            status=False,
                            code=ResponseCode.FAILURE,
                            data=StudentSeminarNode,
                            message="This Seminar already exist for the Student"
                        )
                    student_seminar = StudentSeminar(
                        title=inputItem.title,
                        seminar_date=inputItem.seminar_date,
                        is_pass=inputItem.is_pass,
                        seminar_marks=inputItem.seminar_marks,
                        student_uid=inputItem.student_uid,
                        seminar_types=seminar_type,
                        description=inputItem.description,
                        status=inputItem.status,
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
                            data=student_seminar_list,
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
