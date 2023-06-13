from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

from src.db.session import session_scope
from src.models import ExamCategoryGroup
from src.models.exam_category import ExamCategory
from src.modules.exam_category_groups.service import ExamCategoryGroupsService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ExamCategoryInput, ExamCategoryNode
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import joinedload


class ExamCategoryService(object):
    @staticmethod
    def get_exam_categories() -> List[ExamCategory]:
        with session_scope() as session:
            result = session.query(ExamCategory).filter(ExamCategory.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_exam_categories_by_code(code: List[str]) -> List[ExamCategory]:
        """
            Get Exam Categories by code
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCategory).where(
                (ExamCategory.code.in_(code)) & (ExamCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_exam_categories_by_uid(uid: str) -> ExamCategory:
        """
            Get Exam Categories by uid
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCategory).where(
                (ExamCategory.uid == uid) & (ExamCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_exam_categories_by_uids(uids: List[str]) -> List[ExamCategory]:
        """
            Get Examination Categories by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCategory).where((ExamCategory.uid.in_(uids)) & (ExamCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_exam_categories_by_name(name: str) -> ExamCategory:
        """
            Get Exam Categories by name
        :param:
        :return:
        """
        with session_scope() as session:
            stmt = select(ExamCategory).where(
                (ExamCategory.name == name) & (ExamCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_exam_categories(self, inputs: list[ExamCategoryInput]) -> Response[List[ExamCategoryNode]]:
        """
        Register Exam Category
        :param inputs:
        :return:
        """
        exam_categories_list = []
        with session_scope() as session:
            # Check if Exam Category already exists using code
            existing_codes = [exam_categories.code for exam_categories in session.query(ExamCategory).all()]
            duplicate_categories = [exam_categories for exam_categories in inputs if
                                    exam_categories.code in existing_codes and exam_categories.uid is None]
            if duplicate_categories:
                return Response(
                    status=False,
                    code=ResponseCode.DUPLICATE,
                    data=[],
                    message="Exam Categories Already Exist",
                )

            existed_exam_categories = self.get_exam_categories_by_uids([item.uid for item in inputs])

            for inputItem in inputs:
                try:
                    exam_category_group = ExamCategoryGroupsService.get_exam_category_groups_by_uid(inputItem.exam_category_group_uid)
                    if exam_category_group is None:
                        raise ValueError("You have submitted incorrect exam category group details")
                except Exception as e:
                    print(e)
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    data=[],
                                    message="You have submitted incorrect exam category group details")

                if inputItem.uid is None:
                    exam_category = ExamCategory(
                        code=inputItem.code,
                        name=inputItem.name,
                        exam_category_group=exam_category_group,
                    )
                    local_object = session.merge(exam_category)
                    session.add(local_object)
                    session.commit()
                    exam_categories_list.append(local_object)
                else:
                    exam_category = next(
                        filter(lambda exam_categories: str(exam_categories.uid) == str(inputItem.uid),
                               existed_exam_categories), None
                    )

                    if exam_category:
                        obj_data = jsonable_encoder(inputItem)
                        # # Replace referenced uids field with model required ids field
                        obj_data['exam_category_group'] = exam_category_group
                        for key, value in obj_data.items():
                            setattr(exam_category, key, value)
                        local_object = session.merge(exam_category)
                        session.add(local_object)
                        session.commit()
                        exam_categories_list.append(local_object)

            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                data=exam_categories_list,
                message="Successfully Submitted",
            )

    @staticmethod
    def remove_exam_categories(uid: str):
        """
        Remove Exam Category by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(ExamCategory).filter_by(uid=uid).update({ExamCategory.deleted_at: pendulum.now()})
            session.commit()
