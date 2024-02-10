from typing import List

import pendulum
from sqlalchemy import select, desc
from src.db.session import session_scope
from src.models import ProgramCategory
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCategoryInput, ProgramCategoryListNode


class ProgramCategoryService(CRUDBase[ProgramCategory, ProgramCategoryInput, ProgramCategoryInput]):
    @staticmethod
    def get_program_categories() -> List[ProgramCategory]:
        with session_scope() as session:
            result = session.query(ProgramCategory.name,
                                   ProgramCategory.short_name,
                                   ProgramCategory.uid
                                   ).filter(ProgramCategory.deleted_at.is_(None)).order_by(
                desc(ProgramCategory.updated_at)).all()
            return result

    @staticmethod
    def get_program_categories_by_ids(ids: List[str]) -> List[ProgramCategory]:
        """
        Get programs categories by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCategory).where(
                (ProgramCategory.id.in_(ids)) & (ProgramCategory.deleted_at.is_(None))).order_by(
                desc(ProgramCategory.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_categories_by_uids(uids: List[str]) -> List[ProgramCategory]:
        """
        Get programs category by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCategory).where(
                (ProgramCategory.uid.in_(uids)) & (ProgramCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_category_by_uid(uid: str) -> ProgramCategory:
        """
        Get program category  by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCategory).where((ProgramCategory.uid == uid) & (ProgramCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_program_categories_by_names(names: List[str]) -> List[ProgramCategory]:
        """
        Get programs category by name
        :param names:
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCategory).where(
                (ProgramCategory.name.in_(names)) & (ProgramCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    def register_program_categories(self, inputs: List[ProgramCategoryInput]) -> Response[ProgramCategoryListNode]:
        """
        Register programs categories
        :param inputs:
        :return Response[List[ProgramCategoryNode]]:
        """
        program_category_list = []
        action_type = "Register"
        with session_scope() as session:
            # Check if the program category already exist using uid
            existed_program_category_list = self.get_program_categories_by_names(
                [program_category.name for program_category in inputs if program_category.uid is None])
            if existed_program_category_list:
                return Response(status=False, code=ResponseCode.DUPLICATE,
                                data=ProgramCategoryListNode(items=existed_program_category_list, total_count=0),
                                message="Program Category Already Exists")
            # check for existing programs categories using uid
            existed_program_category = self.get_program_categories_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    program_category = ProgramCategory(
                        name=inputItem.name,
                        short_name=inputItem.short_name
                    )
                    program_category_list.append(program_category)
                else:
                    action_type = "Update"
                    program_category = next(
                        filter(lambda program_category: str(program_category.uid) == str(inputItem.uid),
                               existed_program_category), None)

                    if program_category:
                        program_category.name = inputItem.name
                        program_category.short_name = inputItem.short_name
                        program_category_list.append(program_category)
            session.add_all(program_category_list)
            count = session.query(ProgramCategory).filter(ProgramCategory.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=ProgramCategoryListNode(items=program_category_list, total_count=count),
                            message=f"Successfully to {action_type} Program category")

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


ProgramCategoryCrud = ProgramCategoryService(ProgramCategory)
