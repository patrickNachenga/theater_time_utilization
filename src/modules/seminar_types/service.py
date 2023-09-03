from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc

from src.db.session import session_scope
from src.models.seminar_types import SeminarTypes
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import SeminarTypesInput, SeminarTypesNode, SeminarTypesListNode


class SeminarTypesService(CRUDBase[SeminarTypes, SeminarTypesInput, SeminarTypesInput]):
    @staticmethod
    def get_seminar_types() -> List[SeminarTypes]:
        with session_scope() as session:
            result = session.query(SeminarTypes).filter(SeminarTypes.deleted_at.is_(None)).order_by(
                desc(SeminarTypes.updated_at)).all()
            return result

    @staticmethod
    def get_seminar_types_by_names(names: List[str]) -> List[SeminarTypes]:
        """
        Get seminar Type by names
        :return:
        """
        with session_scope() as session:
            stmt = select(SeminarTypes).where(
                (SeminarTypes.name.in_(names)) & (SeminarTypes.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_seminar_types_by_uids(uids: List[str]) -> List[SeminarTypes]:
        """
        Get Seminar Types by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(SeminarTypes).where((SeminarTypes.uid.in_(uids)) & (SeminarTypes.deleted_at.is_(None))).order_by(
                desc(SeminarTypes.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_seminar_type_by_uid(uid: str) -> SeminarTypes:
        """
        Get seminar_type by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(SeminarTypes).where((SeminarTypes.uid == uid) & (SeminarTypes.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_seminar_types(self, inputs: List[SeminarTypesInput]) -> Response[SeminarTypesNode]:
        """
        Register Seminar Types
        :param inputs:
        :return:
        """
        seminar_type_list = []
        action_name = "Register"
        with session_scope() as session:
            # Check if the Seminar Type already exist using uid
            existed_seminar_type_list = self.get_seminar_types_by_names(
                [seminar_types.name for seminar_types in inputs if seminar_types.uid is None])
            if existed_seminar_type_list:
                return Response(status=False, code=ResponseCode.DUPLICATE,
                                data=SeminarTypesNode(items=existed_seminar_type_list, total_count=0),
                                message="Seminar Type Already Exists")
            # check for existing seminar types using uid
            existed_course_category = self.get_seminar_types_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    seminar_types = SeminarTypes(
                        name=inputItem.name,
                        description=inputItem.description,
                    )
                    seminar_type_list.append(seminar_types)
                else:
                    action_name = "Update"
                    seminar_types = next(
                        filter(lambda seminar_types: str(seminar_types.uid) == str(inputItem.uid),
                               existed_course_category), None)
                    if seminar_types:
                        obj_data = jsonable_encoder(inputItem)
                        for key, value in obj_data.items():
                            setattr(seminar_types, key, value)
                        seminar_type_list.append(seminar_types)
            session.add_all(seminar_type_list)
            count = session.query(SeminarTypes).filter(SeminarTypes.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=SeminarTypesNode(items=seminar_type_list, total_count=count),
                            message=f"Successfully to {action_name} Seminar Type")

    # Delete Function
    @staticmethod
    def remove_seminar_type(uid: str):
        """
        Remove seminar type by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(SeminarTypes).filter_by(uid=uid).update({SeminarTypes.deleted_at: pendulum.now()})
            session.commit()


SeminarTypesCrud = SeminarTypesService(SeminarTypes)
