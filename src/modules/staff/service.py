from typing import List

from sqlalchemy import select

from src.db.session import session_scope
from src.models.staff import Staff
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StaffInput, StaffNode


class StaffService(object):
    @staticmethod
    def get_staffs() -> List[Staff]:
        with session_scope() as session:
            result = session.query(
                Staff.id,
                Staff.pf_number,
                Staff.created_at,
                Staff.updated_at,
            ).filter(Staff.deleted_at.is_(None)).all()
            return result

    @staticmethod
    def get_staffs_by_pf_numbers(pf_numbers: List[str]) -> List[Staff]:
        """
            Get Staffs by pf_nos
        :return:
        """
        with session_scope() as session:
            stmt = select(Staff).where((Staff.pf_number.in_(pf_numbers)) & (Staff.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_staffs_by_uids(uids: List[str]) -> List[Staff]:
        """
            Get Staffs by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(Staff).where((Staff.uid.in_(uids)) & (Staff.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_staff_by_pf_number(pf_number: str) -> Staff:
        """
        Get Staff by pf_number
        :param staff_number:
        :return:
        """
        with session_scope() as session:
            stmt = select(Staff).where((Staff.pf_number == pf_number) & (Staff.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_staffs(self, inputs: List[StaffInput]) -> Response[List[StaffNode]]:
        """
        Register Staff
        :param inputs:
        :return:
        """
        staff_list = []
        with session_scope() as session:
            # Check if staff already exist using pf_number
            existed_staff_list = self.get_staffs_by_pf_numbers(
                [staff.pf_number for staff in inputs if staff.uid is None])
            if existed_staff_list:
                return Response(status=False, code=ResponseCode.DUPLICATE, data=existed_staff_list,
                                message="Staff Already Exists")
            # check for existing Users using uid
            existed_staff = self.get_staffs_by_uids([input.uid for input in inputs])
            for inputItem in inputs:
                if inputItem.uid is None:
                    staff = Staff(pf_number=inputItem.pf_number)
                    staff_list.append(staff)
                else:
                    staff = next(filter(lambda staff: str(staff.uid) == str(inputItem.uid),
                                        existed_staff), None)

                    if staff:
                        staff.pf_number = inputItem.pf_number
                        staff_list.append(staff)
            session.add_all(staff_list)
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS, data=staff_list,
                            message="Successfully Submitted")
