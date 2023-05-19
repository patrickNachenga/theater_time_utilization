from typing import List

from sqlalchemy import select

from src.db.session import session_scope
from src.models.program_category import ProgramCategory
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCategoryInput, ProgramCategoryNode


class ProgramCategoryService(object):
    @staticmethod
    def get_program_category() -> List[ProgramCategory]:
        with session_scope() as session:
            result = session.query(
                ProgramCategory.id,
                ProgramCategory.reg_no,
                ProgramCategory.created_at,
                ProgramCategory.updated_at,
            ).filter(ProgramCategory.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_program_categories_by_ids(ids: List[str]) -> List[ProgramCategory]:
        """
        Get program_categories by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCategory).where((ProgramCategory.in_(ids)) & (ProgramCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_category_id(id: str) -> ProgramCategory:
        """
        Get program category by id
        :param id:
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCategory).where((ProgramCategory.id == id) & (ProgramCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_program_categories(self, inputs: List[ProgramCategoryInput]) -> Response[List[ProgramCategoryNode]]:
        """
        Register Program Category
        :param inputs:
        :return:
        """
        program_category_list = []
        with session_scope() as session:
            # Check if program_category already exist using id
            existed_program_category_list = self.get_program_categories_by_ids(
                [program_category_list.id for program_category in inputs if program_category.uid is None])
            if existed_program_category_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_program_category_list,
                                message="Program Category Already Exists")

            # create new program categories
            for item in inputs:
                program_category = ProgramCategory(id=item.id)
                program_category_list.append(program_category)

            session.add_all(program_category_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=program_category_list,
                            message="Successfully Submitted")
