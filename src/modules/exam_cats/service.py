from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models.exam_category import ExamCats
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamCatsInput, ExamCatsNode


class ExamCatsService(object):
    @staticmethod
    def get_exam_cats() -> List[ExamCats]:
        with session_scope() as session:
            result = session.query(
                ExamCats.id,
                ExamCats.uid,
                ExamCats.code,
                ExamCats.name,
                ExamCats.exam_group_id,
                ExamCats.created_at,
                ExamCats.updated_at,
            ).filter(ExamCats.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_exam_cats_by_code(code: List[str]) -> List[ExamCats]:
        """
            Get Exam Category by code
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCats).where(
                (ExamCats.code.in_(code)) & (ExamCats.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_exam_cats_by_uids(uids: List[str]) -> List[ExamCats]:
        """
            Get Examination by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCats).where((ExamCats.uid.in_(uids)) & (ExamCats.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_exam_cats_by_name(name: str) -> ExamCats:
        """
        Get Exam Category by name
        :param:
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCats).where(
                (ExamCats.name == name) & (ExamCats.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_get_exam_cats(self, inputs: List[ExamCatsInput]) -> Response[List[ExamCatsNode]]:
        """
        Register Exam Category
        :param inputs:
        :return:
        """
        exam_cats_list = []
        with session_scope() as session:
            # Check if Exam Category already exist using programme_number
            existed_exam_cats_list = self.get_exam_cats_by_code(
                [ExamCats.code for exam_cats in inputs if exam_cats.uid is None])
            if existed_exam_cats_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_exam_cats_list,
                                message="Exam Cats Already Exists")
            # check for existing Programme using uid
            existed_exam_cats = self.get_exam_cats_by_uids([item.uid for item in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    exam_cats = ExamCats(
                        code=inputItem.code,
                        name=inputItem.name,
                        exam_group_id=inputItem.exam_group_id,
                    )
                    exam_cats_list.append(exam_cats)
                else:
                    exam_cats = next(filter(lambda exam_cats: str(exam_cats.uid) == str(inputItem.uid),
                                            existed_exam_cats), None)
                    # exam_cats.code = inputItem.code,

                    if exam_cats:
                        exam_cats.code = inputItem.code,
                        exam_cats.name = inputItem.name,
                        exam_cats.exam_group_id = inputItem.exam_group_id,
                        exam_cats_list.append(exam_cats)
            session.add_all(exam_cats_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=exam_cats_list,
                            message="Successfully Submitted")

    @staticmethod
    def remove_exam_cats(uid: str):
        """
        Remove Exam Category by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(ExamCats).filter_by(uid=uid).update({ExamCats.deleted_at: pendulum.now()})
            session.commit()
