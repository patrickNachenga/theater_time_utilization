import json
import uuid
from typing import List

import pendulum
import requests
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc, and_, inspect, String, cast, or_
from sqlalchemy.orm import joinedload

from src.core.security import Info
from src.core.config import settings
from src.db.session import session_scope
from src.models.student_manuscript import StudentManuscript
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentManuscriptInput, StudentManuscriptNode


class StudentManuscriptService(CRUDBase[StudentManuscript, StudentManuscriptInput, StudentManuscriptNode]):

    @staticmethod
    def get_student_manuscript_by_student_uid(student_uid) -> List[StudentManuscript]:
        """
        Get Student Manuscript  by Student Uid
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentManuscript).where((
                               StudentManuscript.student_uid == student_uid) & (
                           StudentManuscript.deleted_at.is_(None)))
            result = session.scalars(stmt)

            return result.all()

    @staticmethod
    def check_uniqueness(student_uid: str, title: str) -> StudentManuscript:
        """
        Check if there already exists Student Manuscript with same title exist,
        :return StudentManuscript:
        """
        with session_scope() as session:
            stmt = select(StudentManuscript).where(
                (StudentManuscript.title == title) &
                (StudentManuscript.student_uid == student_uid) &
                (StudentManuscript.deleted_at.is_(None))
            )
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_student_manuscript() -> Response[StudentManuscript]:
        """
        Get seminar manuscript
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentManuscript).where((StudentManuscript.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_student_manuscript_by_uid(uid: str) -> Response[StudentManuscript]:
        """
        Get seminar_type by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentManuscript).where(
                (StudentManuscript.uid == uid) & (StudentManuscript.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_student_manuscript_by_uids(uids: List[str]) -> List[StudentManuscript]:
        """
        Get Student Manuscript by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentManuscript).where(
                (StudentManuscript.uid.in_(uids)) & (StudentManuscript.deleted_at.is_(None))).order_by(
                desc(StudentManuscript.updated_at))
            result = session.scalars(stmt)
            return result.all()

    def register_student_manuscript(self, inputs: List[StudentManuscriptInput]) -> Response[StudentManuscriptNode]:
        """
        Register Student Manuscript Types
        :param inputs:
        :return:
        """
        student_manuscript_list = []
        action_name = "Register"
        with session_scope() as session:
            existed_student_manuscript = self.get_student_manuscript_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:

                print(inputItem.student_uid)
                print(inputItem.title)
                student_seminar_exist = self.check_uniqueness(student_uid=inputItem.student_uid,
                                                              title=inputItem.title)

                if inputItem.uid is None:
                    if student_seminar_exist:
                        return Response(
                            status=False,
                            code=ResponseCode.DUPLICATE,
                            data=StudentManuscriptNode,
                            message="This Student Manuscript Title already exist for the Student"
                        )
                    student_manuscript = StudentManuscript(
                        title=inputItem.title,
                        publication_date=inputItem.publication_date,
                        publication_status=inputItem.publication_status,
                        student_uid=inputItem.student_uid,
                        description=inputItem.description,
                        status=inputItem.status,
                    )
                    student_manuscript_list.append(student_manuscript)
                else:
                    action_name = "Update"
                    student_manuscript = next(
                        filter(lambda student_manuscript: str(student_manuscript.uid) == str(inputItem.uid),
                               existed_student_manuscript), None)
                    if student_manuscript:
                        obj_data = jsonable_encoder(inputItem)
                        for key, value in obj_data.items():
                            setattr(student_manuscript, key, value)
                        student_manuscript_list.append(student_manuscript)
            session.add_all(student_manuscript_list)
            count = session.query(StudentManuscript).filter(StudentManuscript.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=student_manuscript,
                            message=f"Successfully to {action_name} Student Manuscript")

    # Delete Function
    @staticmethod
    def remove_student_manuscript(uid: str):
        """
        Remove Student Manuscript by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(StudentManuscript).filter_by(uid=uid).update({StudentManuscript.deleted_at: pendulum.now()})
            session.commit()


StudentManuscriptCrud = StudentManuscriptService(StudentManuscript)
