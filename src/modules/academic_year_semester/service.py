from typing import List

import pendulum
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc

from src.db.session import session_scope
from src.models.academic_year_semester import AcademicYearSemester
from src.modules import CRUDBase
from src.modules.academic_year.service import AcademicYearService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import AcademicYearSemesterInput, AcademicYearSemesterListNode


class AcademicYearSemesterService(CRUDBase[AcademicYearSemester, AcademicYearSemesterInput, AcademicYearSemesterInput]):
    @staticmethod
    def get_academic_year_semesters() -> List[AcademicYearSemester]:
        with session_scope() as session:
            result = session.query(AcademicYearSemester).filter(AcademicYearSemester.deleted_at.is_(None)).order_by(
                desc(AcademicYearSemester.updated_at)).all()
            return result

    @staticmethod
    def get_academic_year_semesters_by_uids(uids: List[str]) -> List[AcademicYearSemester]:
        """
        Get Academic Years by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(AcademicYearSemester).where(
                (AcademicYearSemester.uid.in_(uids)) & (AcademicYearSemester.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_academic_year_semesters_by_uid(uid: str) -> AcademicYearSemester:
        """
        Get Academic Year Semester
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(AcademicYearSemester).where(
                (AcademicYearSemester.uid == uid) & (AcademicYearSemester.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_academic_year_semesters_by_academic_year(academic_year_uid: str) -> Response[List[AcademicYearSemester]]:
        """
        Get Academic Year Semester by academic year uid
        :param academic_year_uid:
        :return:
        """
        with session_scope() as session:
            try:
                academic_year = AcademicYearService.get_academic_year_by_uid(academic_year_uid)
                if academic_year is None:
                    raise ValueError("You have submitted incorrect Academic Year values")
            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    data=[],
                    message="You have submitted incorrect Academic Year values"
                )

            stmt = select(AcademicYearSemester).where(
                (AcademicYearSemester.academic_year_id == academic_year.id) & (
                    AcademicYearSemester.deleted_at.is_(None)))
            raw_result = session.scalars(stmt)
            result = raw_result.all()
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                data=result,
                message="You have submitted incorrect Academic Year values"
            )

    def register_academic_semesters(self, inputs: List[AcademicYearSemesterInput]) -> Response[
        AcademicYearSemesterListNode]:
        """
        Register Academic Year Semester
        :param inputs:
        :return:
        """
        academic_year_semester_list = []
        action_type = "Register"
        with session_scope() as session:
            # check for existing Academic Year Semester using uid
            existed_academic_year_semester = self.get_academic_year_semesters_by_uids(
                [inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                try:
                    academic_year = AcademicYearService.get_academic_year_by_uid(inputItem.academic_year_uid)
                    if academic_year is None:
                        raise ValueError("You have submitted incorrect Academic Year values")
                except Exception as e:
                    print(e)
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=AcademicYearSemesterListNode(items=[], total_count=0),
                        message="You have submitted incorrect Academic Year values"
                    )

                if inputItem.uid is None:
                    academic_year_semester = AcademicYearSemester(
                        odd_start_date=inputItem.odd_end_date,
                        odd_end_date=inputItem.odd_start_date,
                        even_start_date=inputItem.even_start_date,
                        even_end_date=inputItem.even_end_date,
                        exam_start_date=inputItem.exam_start_date,
                        exam_ticket_date=inputItem.exam_ticket_date,
                        semester=inputItem.semester,
                        academic_year=academic_year,
                    )
                    local_object = session.merge(academic_year_semester)
                    session.add(local_object)
                    session.commit()
                    academic_year_semester_list.append(local_object)
                else:
                    action_type = "Update"
                    academic_year_semester = next(
                        filter(lambda academic_year_semester_data: str(academic_year_semester_data.uid) == str(
                            inputItem.uid),
                               existed_academic_year_semester), None)
                    if academic_year_semester:
                        obj_data = jsonable_encoder(inputItem)
                        # # Replace referenced uids field with model required ids field
                        obj_data['academic_year'] = academic_year
                        for key, value in obj_data.items():
                            setattr(academic_year_semester, key, value)

                        local_object = session.merge(academic_year_semester)
                        session.add(local_object)
                        session.commit()
                        academic_year_semester_list.append(local_object)
                count = session.query(AcademicYearSemester).filter(AcademicYearSemester.deleted_at.is_(None)).count()
                return Response(status=True, code=ResponseCode.SUCCESS,
                                data=AcademicYearSemesterListNode(items=academic_year_semester_list, total_count=count),
                                message=f"Successfully to {action_type} Academic Year Semester")

    # Delete Function
    @staticmethod
    def remove_academic_year_semester(uid: str):
        """
        Remove Academic year Semeter by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(AcademicYearSemester).filter_by(uid=uid).update(
                {AcademicYearSemester.deleted_at: pendulum.now()})
            session.commit()


AcademicYearSemesterCrud = AcademicYearSemesterService(AcademicYearSemester)
