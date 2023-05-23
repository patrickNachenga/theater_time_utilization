from typing import List

from sqlalchemy import select

from src.db.session import session_scope
from src.models.exam_cats import ExamCats
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamCatsInput, ExamCatsNode


class ExamCatsService(object):
    @staticmethod
    def get_exam_cats() -> List[ExamCats]:
        with session_scope() as session:
            result = session.query(
                ExamCats.id,
                ExamCats.code,
                ExamCats.name,
                ExamCats.exam_group_id,
                ExamCats.created_at,
                ExamCats.updated_at,
            ).filter(ExamCats.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_exam_cats_by_ids(ids: List[str]) -> List[ExamCats]:
        """
        Get exam_cats by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCats).where((ExamCats.id.in_(ids)) & (ExamCats.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()


    @staticmethod
    def get_exam_cats_by_uids(uids: List[str]) -> ExamCats:
        """
        Get exam_cats by id
        :param id:
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCats).where((ExamCats.uid.in_(uids)) & (ExamCats.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_exam_cats_by_code(code: str) -> ExamCats:
        """
        Get exam_cats by code
        :param code:
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCats).where((ExamCats.code == code) & (ExamCats.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_exam_cats_by_name(name: str) -> ExamCats:
        """
        Get exam_cats by name
        :param name:
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCats).where((ExamCats.name == name) & (ExamCats.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_exam_cats(self, inputs: List[ExamCatsInput]) -> Response[List[ExamCatsNode]]:
        """
        Register Program Category
        :param inputs:
        :return:
        """
        exam_cats_list = []
        with session_scope() as session:
            # Check if exam_cats already exist using id
            #existed_exam_cats_list = self.get_exam_cats_by_uids(
            #   [exam_cats.id for exam_cats in inputs if exam_cats.uid is None])
            #if existed_exam_cats_list:
            #    return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_exam_cats_list,
            #                    message='Exam Category Already Exists')

            existed_exam_cats = self.get_exam_cats_by_ids([item.uid for item in inputs])
            if existed_exam_cats:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_exam_cats,
                                message='Exam Category Already Exists')

            # create new exam cat group
            for inputItem in inputs:
                if inputItem.uid is None:
                    exam_cats = ExamCats(
                        name=inputItem.name,
                        exam_group_id=inputItem.exam_group_id,
                        code=inputItem.code
                    )
                    exam_cats_list.append(exam_cats)
                else:
                    exam_cats = next(filter(lambda exam_cats: str(exam_cats.uid) == str(inputItem.uid),existed_exam_cats), None)

                    if exam_cats:
                        exam_cats.name = inputItem.name,
                        exam_cats.id   = inputItem.id,
                        exam_cats.code = inputItem.code,
                        exam_cats.exam_group_id = inputItem.exam_group_id,
                        exam_cats_list.append(exam_cats)
            session.add_all(exam_cats_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=exam_cats,
                            message="Successfully Submitted")