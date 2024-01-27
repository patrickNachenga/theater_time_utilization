from datetime import datetime
from typing import List, Any

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, update

from src.db.session import session_scope
from src.models import AcademicYear, AcademicYearSemester
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import AcademicYearInput, AcademicYearListNode


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
            stmt = select(AcademicYear.name, AcademicYear.id, AcademicYear.uid, AcademicYear.status, AcademicYear.start_date).where((AcademicYear.uid == uid) & (AcademicYear.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_active_academic_year() -> AcademicYear:
        """
        Get Active Academic Year
        :param:
        :return:
        uid: str
    name: str
    status: int
    start_date: str
    end_date: str
        """
        with session_scope() as session:
            # stmt = select(AcademicYear.id, AcademicYear.name, AcademicYear.uid, AcademicYear.status,
            #               AcademicYear.start_date, AcademicYear.end_date).where(
            #     (AcademicYear.status == 1) & (AcademicYear.deleted_at.is_(None)))
            # result = session.scalars(stmt)
            result = session.query(AcademicYear.id, AcademicYear.name, AcademicYear.uid, AcademicYear.status,
                                   AcademicYear.start_date, AcademicYear.end_date).filter(
                AcademicYear.status == 1, AcademicYear.deleted_at.is_(None))

            return result.first()

    def register_academic_year(self, inputs: List[AcademicYearInput]) -> Response[AcademicYearListNode]:
        """
        Register Academic Year
        :param inputs:
        :return:
        """
        academic_year_list = []
        status_checkup = True  # used for onetime check on all supplied academic year status from inputs
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
                # Through an Exception that may be occurred during verification of user inputs
                try:
                    start_date = datetime.strptime(inputItem.start_date, "%Y-%m-%d")
                    end_date = datetime.strptime(inputItem.end_date, "%Y-%m-%d")
                    # Check if inputs has value of start year that great than end year and through an exception
                    if start_date > end_date:
                        return Response(status=False, code=ResponseCode.INVALID_REQUEST,
                                        data=AcademicYearListNode(items=[], total_count=0),
                                        message="End year must be great than Start year to all inputs")
                    # Apply one time check of all inputs status to decide return/pass the operation
                    if status_checkup:
                        status_checkup = False
                        status_list = [item.status for item in inputs if item.status == 1]
                        if len(status_list) > 1:
                            return Response(status=False, code=ResponseCode.INVALID_REQUEST,
                                            data=AcademicYearListNode(items=[], total_count=0),
                                            message="Only one active Academic year are Accepted")
                        else:
                            if len(status_list) == 1:
                                session.query(AcademicYear).filter(AcademicYear.status == 1).update({"status": 0})
                except Exception as e:
                    print(e)
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    data=AcademicYearListNode(items=[], total_count=0),
                                    message="Unable to register Academic year")

                if inputItem.uid is None:
                    academic_year = AcademicYear(
                        name=inputItem.name,
                        status=inputItem.status,
                        start_date=inputItem.start_date,
                        end_date=inputItem.end_date,
                    )
                    academic_year_list.append(academic_year)
                else:
                    action_name = "Updated"
                    academic_year = next(filter(lambda academic_year: str(academic_year.uid) == str(inputItem.uid),
                                                existed_academic_year), None)

                    if academic_year:
                        obj_data = jsonable_encoder(inputItem)
                        for key, value in obj_data.items():
                            setattr(academic_year, key, value)
                        academic_year_list.append(academic_year)
            session.add_all(academic_year_list)
            session.commit()
            count = session.query(AcademicYear).filter(AcademicYear.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=AcademicYearListNode(items=academic_year_list, total_count=count),
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
