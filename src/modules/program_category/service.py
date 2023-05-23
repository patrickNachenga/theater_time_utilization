from typing import List

import pendulum
from sqlalchemy import select
from src.db.session import session_scope
from src.models import ProgramCategory
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCategoryInput, ProgramCategoryNode


class ProgramCategoryService(object):
    @staticmethod
    def get_program_categories() -> List[ProgramCategory]:
        with session_scope() as session:
            result = session.query(
                ProgramCategory.id,
                ProgramCategory.pf_number,
                ProgramCategory.created_at,
                ProgramCategory.updated_at,
            ).filter(ProgramCategory.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_program_categories_by_ids(ids: List[str]) -> List[ProgramCategory]:
        """
        Get program categories by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCategory).where((ProgramCategory.id.in_(ids)) & (ProgramCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_categories_by_uids(uids: List[str]) -> List[ProgramCategory]:
        """
        Get program category by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCategory).where(
                (ProgramCategory.uid.in_(uids)) & (ProgramCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    def register_program_categories(self, inputs: List[ProgramCategoryInput]) -> Response[List[ProgramCategoryNode]]:
        """
        Register program categories
        :param inputs:
        :return:


        """
        program_category_list = []
        with session_scope() as session:
            # Check if the program category already exist using uid
            existed_program_category_list = self.get_program_categories_by_uids(
                [program_category.uid for program_category in inputs if program_category.uid is None])
            if existed_program_category_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_program_category_list,
                                message="Program Category Already Exists")
            # check for existing program categories using uid
            existed_program_category = self.get_program_categories_by_uids([input.uid for input in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    program_category = ProgramCategory(uid=inputItem.uid)
                    program_category_list.append(program_category)
                else:
                    program_category = next(
                        filter(lambda program_category: str(program_category.uid) == str(inputItem.uid),
                               existed_program_category), None)

                    if program_category:
                        program_category.uid = inputItem.uid
                        program_category_list.append(program_category)
            session.add_all(program_category_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=program_category_list,
                            message="Successfully Submitted")

    # Delete FUnction
    @staticmethod
    def remove_program_category(uid: str):
        """
        Remove Program Category by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(ProgramCategory).filter_by(uid=uid).update({ProgramCategory.deleted_at: pendulum.now()})
            session.commit()
