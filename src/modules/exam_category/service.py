from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models import ExamCategoryGroup
from src.models.exam_category import ExamCategory
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
        #print("Inputs list:", inputs)

        with session_scope() as session:
            # Check if Exam Category already exists using code
            existing_codes = [exam_categories.code for exam_categories in session.query(ExamCategory).all()]
            duplicate_categories = [exam_categories for exam_categories in inputs if
                                    exam_categories.code in existing_codes]

            if duplicate_categories:
                return Response(
                    status=False,
                    code=ResponseCode.DUPLICATE,
                    data=[],
                    message="Exam Categories Already Exist",
                )

            existed_exam_categories = self.get_exam_categories_by_uids([item.uid for item in inputs])

            for inputItem in inputs:
                print("Input Item:", inputItem)
                exam_category_group = session.query(ExamCategoryGroup).filter(
                    ExamCategoryGroup.uid == inputItem.exam_category_group_uid
                ).first()
                print("Exam Category Group:", exam_category_group)

                if exam_category_group:
                    if inputItem.uid is None:
                        exam_categories = ExamCategory(
                            code=inputItem.code,
                            name=inputItem.name,
                            exam_category_group_id=exam_category_group.id,
                        )
                        exam_categories_list.append(exam_categories)
                    else:
                        exam_categories = next(
                            filter(lambda exam_categories: str(exam_categories.uid) == str(inputItem.uid),
                                   existed_exam_categories), None
                        )

                        if exam_categories:
                            exam_categories.code = inputItem.code
                            exam_categories.name = inputItem.name
                            exam_categories.exam_category_group_id = exam_category_group.id
                            exam_categories_list.append(exam_categories)

                else:
                    return Response(
                        status=False,
                        code=ResponseCode.DUPLICATE,
                        data=duplicate_categories,
                        message="Please used valid exam category details",
                    )
            print("Before commit, exam_categories_list:", exam_categories_list)

            session.add_all(exam_categories_list)
            session.commit()

            print("After commit, exam_categories_list:", exam_categories_list)

            # Refresh the relationships for the newly added instances
            for exam_categories in exam_categories_list:
                session.refresh(exam_categories)

            print("After refresh, exam_categories_list:", exam_categories_list)

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
