from typing import List

import pendulum

from src.db.session import session_scope
from src.models import ByLaw
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ByLawInput, ByLawListNode


class ByLawService(CRUDBase[ByLaw, ByLawInput, ByLawInput]):
    @staticmethod
    def get_by_laws() -> List[ByLaw]:
        with session_scope() as session:
            result = session.query(ByLaw).filter(ByLaw.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_by_law_by_id(id: List[int]) -> List[ByLaw]:
        """
        Get By law by id
        :return:
        """
        with session_scope() as session:
            result = session.query(ByLaw).filter(ByLaw.id == id, ByLaw.deleted_at.is_(None)).first()
            return result

    @staticmethod
    def get_by_law_by_uid(uid: str) -> ByLaw:
        """
        Get Academic Year by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            result = session.query(ByLaw).filter(ByLaw.uid == uid, ByLaw.deleted_at.is_(None)).first()
            return result

    @staticmethod
    def get_active_by_law() -> ByLaw:
        """
        Get Active by law
        :param:
        :return:
        """
        with session_scope() as session:
            result = session.query(ByLaw).filter(ByLaw.status == True, ByLaw.deleted_at.is_(None)).last()

            return result

    def register_by_law(self, inputs: ByLawInput) -> Response[ByLawListNode]:
        """
        Register by law
        :param inputs:
        :return:
        """

        with session_scope() as session:
            by_law = session.query(ByLaw).filter(ByLaw.code == inputs.code, ByLaw.deleted_at.is_(None)).first()
            if by_law:
                by_law.name = inputs.name
                by_law.code = inputs.code
                by_law.status = inputs.status
                by_law.start_date = inputs.start_date
                by_law.end_date = inputs.end_date
            else:
                session.query(ByLaw).update({ByLaw.status: False})

                by_law = ByLaw(
                    name=inputs.name,
                    code=inputs.code,
                    status=inputs.status,
                    start_date=inputs.start_date,
                    end_date=inputs.end_date,
                )
                session.add(by_law)
                session.commit()
                existing_bylaws = session.query(ByLaw).all()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=ByLawListNode(items=existing_bylaws, total_count=len(existing_bylaws)),
                            message=f"By law added Successfully")

    # Delete Function
    @staticmethod
    def remove_by_law(uid: str) -> Response[ByLawListNode]:
        """
        Remove By law UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(ByLaw).filter(ByLaw.uid == uid).update({ByLaw.deleted_at: pendulum.now()})
            session.commit()
            existing_bylaws = session.query(ByLaw).all()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=ByLawListNode(items=existing_bylaws, total_count=len(existing_bylaws)),
                            message=f"By law removed Successfully")


ByLawCrud = ByLawService(ByLaw)
