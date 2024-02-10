from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models import Group
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import GroupInput, GroupNode


class GroupService(object):
    @staticmethod
    def get_groups() -> List[Group]:
        with session_scope() as session:
            result = session.query(
                Group.id,
                Group.uid,
                Group.name,
                Group.code,
                Group.created_at,
                Group.updated_at,
            ).filter(Group.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_groups_by_ids(ids: List[str]) -> List[Group]:
        """
        Get Groups by ids
        :return:
        """
        with session_scope() as session:
            stmt = select(Group).where((Group.id.in_(ids)) & (Group.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_group_by_id(id: str) -> Group:
        """
        Get User by reg_no
        :param id:
        :return:
        """
        with session_scope() as session:
            stmt = select(Group).where((Group.id == id) & (Group.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_groups_by_uids(uids: List[str]) -> List[Group]:
        """
        Get Groups by Uids
        :param uids:
        :return:
        """
        with session_scope() as session:
            stmt = select(Group).where((Group.uid.in_(uids)) & (Group.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_group_by_uid(uid: str) -> Group:
        """
        Get User by reg_no
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(Group).where((Group.uid == uid) & (Group.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_groups_by_codes(codes: List[str]) -> List[Group]:
        """
        Get Groups by Uids
        :param codes:
        :return:
        """
        with session_scope() as session:
            stmt = select(Group).where((Group.code.in_(codes)) & (Group.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_group_by_code(code: str) -> Group:
        """
        Get User by reg_no
        :param code:
        :return:
        """
        with session_scope() as session:
            stmt = select(Group).where((Group.code == code) & (Group.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_groups(self, inputs: List[GroupInput]) -> Response[List[GroupNode]]:
        """
        Register Students
        :param inputs:
        :return:
        """
        group_list = []
        with session_scope() as session:
            # Check if Group already exists using id
            existed_group_list = self.get_groups_by_codes(
                [Group.code for group in inputs if group.uid is None])
            if existed_group_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_group_list,
                                message="Groups Already Exists")
            # check for existing Group using uid
            existed_groups = self.get_groups_by_uids([item.uid for item in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    group = Group(
                        code=inputItem.code,
                        name=inputItem.name,
                    )
                    group_list.append(group)
                else:
                    group = next(filter(lambda group: str(group.uid) == str(inputItem.uid),
                                        existed_groups), None)

                    if group:
                        group.name = inputItem.name,
                        group.code = inputItem.code,
                        group_list.append(group)
            session.add_all(group_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=group_list,
                            message="Successfully Submitted")

    @staticmethod
    def remove_group(uid: str):
        """
        Remove Group by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(Group).filter_by(uid=uid).update({Group.deleted_at: pendulum.now()})
            session.commit()
