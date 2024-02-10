import json
from typing import Optional

import requests
import strawberry

from src.core.config import settings
from src.core.security import CustomPermissionExtension
from src.modules.semester_registration.service import SemesterRegistrationService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import PaginationInput, SemesterRegistrationListNode, RegisteredStudentNode, RegisteredStudentListNode


@strawberry.type
class SemesterRegistrationQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_STUDENT_SEMESTER_REGISTRATIONS"])])
    def get_semester_registrations(self, pagination: PaginationInput) -> Response[SemesterRegistrationListNode]:
        try:
            result = SemesterRegistrationService().get_semester_registrations(pagination)
        except Exception as e:
            print(e)
            result = SemesterRegistrationListNode(items=[], total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve semester registration",
            data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_STUDENT_SEMESTER_REGISTRATIONS"])])
    def get_student_semester_registrations(self, student_uid: str) -> Response[SemesterRegistrationListNode]:
        try:
            result = SemesterRegistrationService().get_student_semester_registrations(student_uid)
        except Exception as e:
            print(e)
            result = SemesterRegistrationListNode(items=[], total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve semester registrations",
            data=result)

    @strawberry.field()
    def get_registered_students(self) -> Response[bool]:
        try:
            result = SemesterRegistrationService().get_registered_students()
        except Exception as e:
            print(e)
            result = False
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve registrations",
            data=True)

    @strawberry.field()
    def get_registered_students_plan_B(self) -> Response[RegisteredStudentListNode]:
        try:
            result = SemesterRegistrationService().get_registered_students_plan_B()

            student_uids = [semester_registration.student_uid for semester_registration in result]
            data = None
            data_obj = {
                "uids": student_uids
            }
            try:
                # Serialize the data to JSON
                data_json = json.dumps(data_obj)

                # Set the Content-Type header to indicate that the request body is JSON
                headers = {
                    "Content-Type": "application/json"
                }

                response = requests.post(settings.UAA_URi + '/students-details-by-uids', data=data_json,
                                         headers=headers)


            except Exception as e:
                print(e)
                response = None
            list_node = []
            if response.status_code == 200:
                response_data = response.json()
                for semester_registration in result:
                    student_uid = semester_registration.student_uid
                    # Search for student information in the response data by matching student_uid
                    student_info = response_data.get(student_uid)
                    st_node = RegisteredStudentNode(
                        registration_number=student_info.get('registration_number'),
                        full_name=student_info.get('full_name'),
                        year_of_study=semester_registration.study_year,
                        program_code=semester_registration.semester_program.program.code,
                        academic_year=semester_registration.semester_program.academic_year.name,
                        semester=semester_registration.semester_program.semester,
                    )
                    list_node.append(st_node)
                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Successfully Retrieve registered students",
                    data=RegisteredStudentListNode(items=list_node,total_count=len(list_node)))

        except Exception as e:
            print(e)
            result = SemesterRegistrationListNode(items=[], total_count=0)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Failed to Retrieve semester registrations",
                data=result)
