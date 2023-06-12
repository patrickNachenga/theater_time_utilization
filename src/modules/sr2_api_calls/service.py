from typing import List, Optional
from urllib.parse import urlencode

import requests
from sqlalchemy import desc, select

from src.db.session import session_scope
from src.models import Program
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import FeeStructureInput, RequestControlNumberInput, ControlNumberNode, RewControlNumberInput
from src.types import FeeStructureNode


class Sr2ApiCalls(object):
    token = '9454c6efdb94236e618c9a7b1a67138b'
    site_url = 'http://197.250.34.41:4747/api/v2/'

    @staticmethod
    def get_fee_structures(inputs: FeeStructureInput) -> Response[List[FeeStructureNode]] | None:
        """
        This is a function to request program fee structure  from SR2
        """
        # Verify and get supplied Program code and exists
        with session_scope() as session:
            program = session.query(Program).filter_by(uid=inputs.program_uid).first()
            if not program:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None, message="Program Not Found")

            # Set the request payload
            payload = {
                "program_code": program.code,
                "year_of_study": inputs.year_of_study,
                "study_level": program.program_category.short_name,
                "student_status": inputs.student_status,
                "countrycode": inputs.countrycode,
            }
            encoded_params = urlencode(payload)
            # Send the Get request
            response = requests.get(Sr2ApiCalls.site_url + f"billing/program_fee_structure?{encoded_params}")
            # Check for errors
            if response.status_code == 200:
                response_data = response.json()
                fee_structure_list = []
                for structure in response_data["data"]:
                    fee_structure = FeeStructureNode(
                        name=structure["fee_name"],
                        amount=float(structure["amount"]),
                        min_amount=float(structure["min_amount"]),
                        currency=structure["currency"],
                        program=program,
                        study_year=inputs.year_of_study
                    )
                    fee_structure_list.append(fee_structure)
                return Response(status=True, code=ResponseCode.SUCCESS,
                                data=fee_structure_list,
                                message="Fee structure for %s was Retrieved Successfully" % program.short_name)

            else:
                print(response)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve fee structure for %s " % program.short_name,
                    data=None)

    @staticmethod
    def request_control_numbers(inputs: RequestControlNumberInput) -> Response[Optional[str]]:

        # Verify and get supplied Program code and exists
        with session_scope() as session:
            program = session.query(Program).filter_by(uid=inputs.program_uid).first()
            if not program:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None, message="Program Not Found")

            # Set the request payload
            payload = {
                "program_code": program.code,
                "study_level": program.program_category.short_name,
                "program_name": program.name,
                "year_of_study": inputs.year_of_study,
                "student_status": inputs.student_status,
                "countrycode": inputs.countrycode,
                "registration_number": inputs.registration_number,
                "system": "uqf",
            }

            # Send the Get request
            response = requests.post(Sr2ApiCalls.site_url + f"billing/program_fee_structure", data=payload)

            # Check for errors
            if response.status_code == 200:
                response_data = response.json()
                # print(response_data["message"])
                return Response(status=True, code=ResponseCode.SUCCESS,
                                data=None, message="Control number request generated successfully")
            else:
                return Response(status=False, code=ResponseCode.FAILURE,
                                data=None, message="Failed to generate control number request")

    @staticmethod
    def renew_control_number(inputs: RewControlNumberInput) -> Response[Optional[str]]:
        # Set the request payload
        payload = {
            "pay_type": inputs.pay_type,
            "registration_number": inputs.registration_number,
            "billid": inputs.bill_id,
            "service+type": "refresh"
        }

        # Send the Get request
        response = requests.post(Sr2ApiCalls.site_url + f"billing/program_fee_structure", data=payload)
        # Check for errors
        if response.status_code == 200:
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=None, message="Request Submitted Successful")
        else:
            return Response(status=False, code=ResponseCode.FAILURE,
                            data=None, message="Failed to refresh number request")



    @staticmethod
    def get_student_control_number(registration_number: str) -> List[ControlNumberNode] | None:
        """
        This is a function to request program fee structure  from SR2
        """
        try:
            # Set the request payload
            payload = {
                "registration_number": registration_number
            }
            encoded_params = urlencode(payload)
            response = requests.get(Sr2ApiCalls.site_url + f"billing/get_control_numbers?{encoded_params}")
            # Check for errors
            if response.status_code == 200:
                response_data = response.json()
                control_number_list = []
                for structure in response_data["data"]:
                    print(structure)
                    control_number = ControlNumberNode(
                        registration_number=structure["registration_number"],
                        fee_name=structure["fee_name"],
                        amount=structure["amount"],
                        control_number=structure["control_number"],
                        currency=structure["currency"],
                        pay_type=structure["pay_type"],
                        academic_year=structure["academic_year"],
                        bill_id=structure["billid"],
                    )
                    control_number_list.append(control_number)
                return control_number_list
            else:
                return None
        except Exception as e:
            print(e)
            return None
