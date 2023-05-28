from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models import AcademicYear
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import AcademicYearInput, AcademicYearNode, AcademicYearListNode


class AcademicYearService(CRUDBase[AcademicYear, AcademicYearInput, AcademicYearInput]):
    @staticmethod
    def get_academic_years() -> List[AcademicYear]:
        with session_scope() as session:
            result = session.query(AcademicYear).filter(AcademicYear.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_academic_year_by_name(name: List[str]) -> List[AcademicYear]:
        """
        Get Academic Year by name
        :return:
        """
        with session_scope() as session:
            stmt = select(AcademicYear).where((AcademicYear.name.in_(name)) & (AcademicYear.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_academic_year_by_id(id: List[int]) -> List[AcademicYear]:
        """
        Get AcademicYear by id
        :return:
        """
        with session_scope() as session:
            stmt = select(AcademicYear).where(
                (AcademicYear.id.in_(id)) & (AcademicYear.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_academic_year_by_uids(uids: List[str]) -> List[AcademicYear]:
        """
        Get Academic Year by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(AcademicYear).where((AcademicYear.uid.in_(uids)) & (AcademicYear.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_academic_year_by_uid(uid: str) -> AcademicYear:
        """
        Get Academic Year by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(AcademicYear).where((AcademicYear.uid == uid) & (AcademicYear.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_academic_year(self, inputs: List[AcademicYearInput]) -> Response[AcademicYearListNode]:
        """
        Register Academic Year
        :param inputs:
        :return:
        """
        academic_year_list = []
        action_name = "Registered"
        with session_scope() as session:
            # Check if the Academic Year already exist using uid
            existed_academic_year_list = self.get_academic_year_by_name(
                [academic_year.name for academic_year in inputs if academic_year.uid is None])
            if existed_academic_year_list:
                return Response(status=False, code=ResponseCode.DUPLICATE,
                                data=AcademicYearListNode(items=existed_academic_year_list, total_count=0),
                                message="One or More Academic Year Already exist")
            # check for existing course using uid
            existed_academic_year = self.get_academic_year_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    academic_year = AcademicYear(
                        name=inputItem.name,
                        status=inputItem.status,
                        start_date=inputItem.start_date,
                        end_date=inputItem.end_date
                    )
                    academic_year_list.append(academic_year)
                else:
                    action_name = "Updated"
                    academic_year = next(filter(lambda academic_year: str(academic_year.uid) == str(inputItem.uid),
                                                existed_academic_year), None)

                    if academic_year:
                        academic_year.name = inputItem.name,
                        academic_year.status = inputItem.status,
                        academic_year.start_date = inputItem.start_date
                        academic_year.end_date = inputItem.end_date,
                        academic_year_list.append(academic_year)
            session.add_all(academic_year_list)
            count = session.query(AcademicYear).filter(AcademicYear.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=AcademicYearListNode(items=academic_year_list, total_count=count),
                            message=f"Academic Year {action_name} Successfully")
    # Delete Function
    @staticmethod
    def remove_academic_year(uid: str):
        """
        Remove Academic Year by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(AcademicYear).filter_by(uid=uid).update({AcademicYear.deleted_at: pendulum.now()})
            session.commit()


AcademicYearCrud = AcademicYearService(AcademicYear)
