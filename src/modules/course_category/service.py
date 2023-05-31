from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

from src.db.session import session_scope
from src.models import ProgramCategory
from src.models.course_category import CourseCategory
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseCategoryInput, CourseCategoryNode


class CourseCategoryService(CRUDBase[CourseCategory, CourseCategoryInput, CourseCategoryInput]):
    @staticmethod
    def get_course_categories() -> List[CourseCategory]:
        with session_scope() as session:
            result = session.query(CourseCategory).filter(CourseCategory.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_course_categories_by_names(names: List[str]) -> List[CourseCategory]:
        """
        Get course categories by names
        :return:
        """
        with session_scope() as session:
            stmt = select(CourseCategory).where(
                (CourseCategory.name.in_(names)) & (CourseCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_course_categories_by_uids(uids: List[str]) -> List[CourseCategory]:
        """
        Get course Categories by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(CourseCategory).where((CourseCategory.uid.in_(uids)) & (CourseCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_course_category_by_uid(uid: str) -> CourseCategory:
        """
        Get course category by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(CourseCategory).where((CourseCategory.uid == uid) & (CourseCategory.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_course_categories(self, inputs: List[CourseCategoryInput]) -> Response[List[CourseCategoryNode]]:
        """
        Register Course Categories
        :param inputs:
        :return:
        """
        course_category_list = []
        action_name = "Register"
        with session_scope() as session:
            # Check if the course already exist using uid
            existed_course_category_list = self.get_course_categories_by_names(
                [course_category.name for course_category in inputs if course_category.uid is None])
            if existed_course_category_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_course_category_list,
                                message="Course Category Already Exists")
            # check for existing course category using uid
            existed_course_category = self.get_course_categories_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    course_category = CourseCategory(
                        name=inputItem.name,
                        description=inputItem.description,
                    )
                    course_category_list.append(course_category)
                else:
                    action_name = "Update"
                    course_category = next(
                        filter(lambda course_category: str(course_category.uid) == str(inputItem.uid),
                               existed_course_category), None)
                    if course_category:
                        obj_data = jsonable_encoder(inputItem)
                        for key, value in obj_data.items():
                            setattr(course_category, key, value)
                        course_category_list.append(course_category)
            session.add_all(course_category_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=course_category_list,
                            message=f"Successfully to {action_name} Course Category")

    # Delete Function
    @staticmethod
    def remove_course_category(uid: str):
        """
        Remove course by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(CourseCategory).filter_by(uid=uid).update({CourseCategory.deleted_at: pendulum.now()})
            session.commit()


CourseCategoryCrud = CourseCategoryService(CourseCategory)
