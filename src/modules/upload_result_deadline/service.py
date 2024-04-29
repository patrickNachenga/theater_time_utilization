from typing import List

import pendulum
import requests
from sqlalchemy import select

from src.core.config import settings
from src.db.session import session_scope
from src.models.upload_result_deadline import UploadResultDeadline
from src.modules.academic_year_semester.service import AcademicYearSemesterService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import UploadResultDeadlineNode


class UploadResultDeadlineService(object):
    @staticmethod
    def get_upload_result_deadline(info) -> List[UploadResultDeadlineNode]:
        with session_scope() as session:
            departments = info.context.user.department_headships
            # print(departments)
            if departments is None:
                return []
            headers = {
                "Content-Type": "application/json"
            }

            query_result = session.query(UploadResultDeadline).filter(
                UploadResultDeadline.department_uid.in_(departments),
                UploadResultDeadline.deleted_at.is_(None)).all()

            if not query_result:
                return []

            return_data = []
            for result in query_result:
                response = requests.get(settings.UAA_URi + f'/department/{result.department_uid}', headers=headers)
                response.raise_for_status()
                if response.status_code != 200:
                    return []
                response_data = response.json()
                if not response_data['status']:
                    return []
                data = response_data['data']
                department_name = data['name']
                return_data.append(UploadResultDeadlineNode(
                    department=department_name,
                    end_date=result.end_date,
                    academic_year_semester=result.academic_year_semester,
                    uid=result.uid
                ))
            return return_data

    @staticmethod
    def register_upload_result_deadline(inputs, info) -> Response[None]:
        add_list = []
        with session_scope() as session:
            if inputs.uid is None:
                departments = info.context.user.department_headships
                if departments is None:
                    return Response(status=False, code=ResponseCode.FAILURE, data=None,
                                    message="You dont have any HOD headship")
                # Check Active Academic Year Semester
                active_semester = AcademicYearSemesterService.get_active_academic_year_semester()
                if active_semester is None:
                    return Response(status=False, code=ResponseCode.FAILURE, data=None,
                                    message="There is no Active Academic Year Semester")
                add_all_list = []
                for department in departments:
                    check_duplicate = session.query(UploadResultDeadline).filter(
                        UploadResultDeadline.department_uid == department).all()
                    if check_duplicate:
                        continue
                    add_all_list.append(UploadResultDeadline(
                        department_uid=department,
                        end_date=inputs.end_date,
                        academic_year_semester_id=active_semester.id
                    ))
                if len(add_all_list) > 0:
                    session.add_all(add_all_list)
                session.commit()
                return Response(status=True, code=ResponseCode.SUCCESS, data=[],
                                message="Successfully Submitted")
            else:
                session.query(UploadResultDeadline).filter_by(uid=inputs.uid) \
                    .update({UploadResultDeadline.end_date: inputs.end_date})
                session.commit()
                return Response(status=True, code=ResponseCode.SUCCESS, data=[],
                                message="Successfully Submitted")

    @staticmethod
    def remove_upload_result_deadline(uid: str):
        """
        Remove Group by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(UploadResultDeadline).filter_by(uid=uid) \
                .update({UploadResultDeadline.deleted_at: pendulum.now()})
            session.commit()
