from typing import List

from sqlalchemy import select

from src.db.session import session_scope
from src.models.group import Group
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import GroupInput, GroupNode


class GroupService(object):
    @staticmethod
    def get_groups() -> List[Group]:
        with session_scope() as session:
            result = session.query(
                Group.id,
                Group.name,
                Group.uid,
                Group.code,
                Group.created_at,
                Group.updated_at,
            ).filter(Group.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_groups_by_uuids(ids: List[str]):
        """
        Get Groups by uuids
        """
        with session_scope() as session:
            stmt = select(Group).where((Group.uid.in_(ids)) & (Group.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_groups_by_code(code: List[str]):
        """
        Get Groups by code
        """
        with session_scope() as session:
            stmt = select(Group).where((Group.code.in_(code)) & (Group.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    def register_groups(self, inputs: List[GroupInput]) -> Response[List[GroupNode]]:
        """
        Register Groups
        :param inputs:
        :return:
        """
        group_list = []
        with session_scope() as session:
            # Check if group already exist using code
            existed_group_list = self.get_groups_by_code(
                [group.code for group in inputs if group.uid is None])
            if existed_group_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_group_list,
                                message="group Already exist")
            # check for existing Groups using uid
            existed_groups = self.get_groups_by_uuids([input.uid for inputItem in inputs])
            # create new groups
            for singleInput in inputs:
                group = Group(code=singleInput.code, name=singleInput.name)
                group_list.append(group)
            session.add_all(group_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=group_list,
                            message="Successfully Submitted")
