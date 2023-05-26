from typing import List

from sqlalchemy import select

from src.db.session import session_scope
from src.models.exam_cat_group import ExamCatGroups
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamCatGroupsInput, ExamCatGroupsNode


class ExamCatGroupsService(object):
    @staticmethod
    def get_exam_cat_groups() -> List[ExamCatGroups]:
        with session_scope() as session:
            result = session.query(
                ExamCatGroups.id,
                ExamCatGroups.name,
                ExamCatGroups.created_at,
                ExamCatGroups.updated_at,
            ).filter(ExamCatGroups.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_exam_cat_groups_by_ids(ids: List[str]) -> List[ExamCatGroups]:
        """
        Get exam_cat_groups by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCatGroups).where((ExamCatGroups.id.in_(ids)) & (ExamCatGroups.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_exam_cat_groups_id(id: str) -> ExamCatGroups:
        """
        Get exam_cat_groups by id
        :param id:
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCatGroups).where((ExamCatGroups.id == id) & (ExamCatGroups.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_exam_cat_groups_by_uids(uids: List[str]) -> List[ExamCatGroups]:
        """
        Get exam_cat_groups by uids
        :param uids:
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCatGroups).where((ExamCatGroups.uid.in_(uids)) & (ExamCatGroups.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_exam_cat_groups_uid(uid: str) -> ExamCatGroups:
        """
        Get exam_cat_groups by id
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCatGroups).where((ExamCatGroups.id == id) & (ExamCatGroups.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_exam_cat_groups(self, inputs: List[ExamCatGroupsInput]) -> Response[List[ExamCatGroupsNode]]:
        """
        Register ExamCatGroup Category
        :param inputs:
        :return:
        """
        exam_cat_groups_list = []
        with session_scope() as session:
            # Check if exam_cat_groups already exist using id
            # existed_exam_cat_groups_list = self.get_exam_cat_groups_by_ids(
            #     [exam_cat_groups.id for exam_cat_groups in inputs if exam_cat_groups.uid is None])
            # if existed_exam_cat_groups_list:
            #     return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_exam_cat_groups_list,
            #                     message="Exam Category Group Already Exists")
            existed_exam_cat_group = self.get_exam_cat_groups_by_uids([item.uid for item in inputs])
            # create new exam cat group
            for inputItem in inputs:
                if inputItem.uid is None:
                    exam_cat_groups = ExamCatGroups(
                        name=inputItem.name
                    )
                    exam_cat_groups_list.append(exam_cat_groups)
                else:
                    exam_cat_groups = next(filter(lambda exam_cat_group: str(exam_cat_group.uid) == str(inputItem.uid),
                                                  existed_exam_cat_group), None)

                    if exam_cat_groups:
                        exam_cat_groups.name = inputItem.name,
                        exam_cat_groups_list.append(exam_cat_groups)
            session.add_all(exam_cat_groups_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=exam_cat_groups_list,
                            message="Successfully Submitted")
