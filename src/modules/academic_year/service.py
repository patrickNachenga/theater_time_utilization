from typing import List

import pendulum
from sqlalchemy import select

from src.db.session import session_scope
from src.models import AcademicYear
from src.models.student import Student
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import AcademicYearInput, AcademicYearNode


class AcademicYearService(object):
    @staticmethod
    def get_academic_year() -> List[AcademicYear]:
        with session_scope() as session:
            result = session.query(
                AcademicYear.id,
                AcademicYear.uid,
                AcademicYear.name,
                AcademicYear.status,
                AcademicYear.start_date,
                AcademicYear.end_date,
            ).filter(AcademicYear.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_academic_year_by_name(name: List[str]) -> List[AcademicYear]:
        """
        Get Academic Year by code
        :return:
        """
        with session_scope() as session:
            stmt = select(AcademicYear).where((AcademicYear.name.in_(name)) & (AcademicYear.deleted_at.is_(None)))
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

    def register_academic_year(self, inputs: List[AcademicYearInput]) -> Response[List[AcademicYearNode]]:
        """
        Register Academic Year
        :param inputs:
        :return:
        """
        academic_year_list = []
        with session_scope() as session:
            # Check if the Academic Year already exist using uid
            existed_academic_year_list = self.get_academic_year_by_name(
                [academic_year.name for academic_year in inputs if academic_year.uid is None])
            if existed_academic_year_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_academic_year_list,
                                message="Academic Year Already Exists")
            # check for existing course using uid
            existed_academic_year = self.get_academic_year_by_name([inputItem.uid for inputItem in inputs])
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
                    academic_year = next(filter(lambda academic_year: str(academic_year.uid) == str(inputItem.uid),
                                         existed_academic_year), None)
                    if academic_year:
                        academic_year.end_date = inputItem.end_date,
                        academic_year.name = inputItem.name,
                        academic_year.status = inputItem.status,
                        academic_year.start_date = inputItem.start_date
                        academic_year_list.append(academic_year)
            session.add_all(academic_year_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=academic_year_list,
                            message="Successfully Submitted Academic Year")

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


