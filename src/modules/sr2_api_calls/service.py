from typing import List, Optional
from urllib.parse import urlencode

import requests

from src.core.config import settings
from src.db.session import session_scope
from src.models import Program
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import FeeStructureInput, RequestControlNumberInput, ControlNumberNode, RewControlNumberInput
from src.types import FeeStructureNode


class Sr2ApiCalls(object):
    token = settings.SR2_TOKEN
    site_url = settings.SR2_SERVICE_URL

    @staticmethod
    def get_fee_structures(inputs: FeeStructureInput) -> Response[List[FeeStructureNode]]:
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
            elif response.status_code == 404:
                return Response(
                    status=False,
                    code=ResponseCode.NO_RECORD_FOUND,
                    message=response.json()["message"],
                    data=None)
            else:
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve fee structure for %s " % program.short_name,
                    data=None)

    @staticmethod
    def request_control_numbers(inputs: RequestControlNumberInput) -> Response[str]:

        # Verify and get supplied Program code and exists
        with session_scope() as session:
            program = session.query(Program).filter_by(uid=inputs.program_uid).first()
            if not program:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None, message="Program Not Found")

            # Set the request payload
            payload = {
                "program_code": program.code,
                "student_name": inputs.student_name,
                "study_level": program.program_category.short_name,
                "program_name": program.name,
                "year_of_study": inputs.year_of_study,
                "student_status": inputs.student_status,
                "countrycode": inputs.countrycode,
                "registration_number": inputs.registration_number,
                "system": "SUA-ESB",
            }

            # Send the Get request
            response = requests.post(Sr2ApiCalls.site_url + f"billing/program_fee_structure", data=payload)

            # Check for errors
            if response.status_code == 200:
                # response_data = response.json()
                # print(response_data["message"])
                return Response(status=True, code=ResponseCode.SUCCESS,
                                data=None, message="Control number request generated successfully")
            elif response.status_code == 400:
                return Response(status=False, code=ResponseCode.INVALID_REQUEST,
                                data=None, message="Your have Submitted Incorrect Request Data")
            else:
                return Response(status=False, code=ResponseCode.FAILURE,
                                data=None, message="Failed to generate control number request")

    @staticmethod
    def renew_control_number(inputs: RewControlNumberInput) -> Response[str]:
        # Set the request payload
        payload = {
            "pay_type": inputs.pay_type,
            "registration_number": inputs.registration_number,
            "billid": inputs.bill_id,
            "service+type": "refresh"
        }

        # Send the Get request
        response = requests.post(Sr2ApiCalls.site_url + f"billing/program_fee_structure", data=payload, timeout=10)
        # Check for errors
        if response.status_code == 200:
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=None, message="Request Submitted Successful")
        else:
            return Response(status=False, code=ResponseCode.FAILURE,
                            data=None, message="Failed to refresh number request")

    @staticmethod
    def get_student_control_number(registration_number: str) -> Response[List[ControlNumberNode]]:
        """
        This is a function to request program fee structure  from SR2
        """
        # Set the request payload
        payload = {
            "registration_number": registration_number
        }
        encoded_params = urlencode(payload)
        response = requests.get(Sr2ApiCalls.site_url + f"billing/get_control_numbers?{encoded_params}", timeout=10)
        # Check for errors
        if response.status_code == 200:
            response_data = response.json()
            control_number_list = []
            for structure in response_data["data"]:
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
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Control Numbers Retrieved successfully",
                data=control_number_list
            )
        else:
            return Response(
                status=True,
                code=ResponseCode.NO_RECORD_FOUND,
                message="No Control Numbers Found",
                data=None
            )

    @staticmethod
    def get_financial_statement(registration_number: str) -> Response[str]:
        """
        This is a function to request student financial statement  from SR2
        """
        # Set the request payload
        payload = {
            "registration_number": registration_number,
            "type": "generate"
        }
        encoded_params = urlencode(payload)
        response = requests.get(Sr2ApiCalls.site_url + f"students/statement?{encoded_params}", timeout=10)
        # Check for errors
        if response.status_code == 200:
            payload["type"] = "get"
            encoded_params = urlencode(payload)
            response = requests.get(Sr2ApiCalls.site_url + f"students/statement?{encoded_params}")
            response_data = response.json()
            # Check for errors
            if response.status_code == 200:
                response_data = response.json()
                return Response(status=True, code=ResponseCode.SUCCESS,
                                data=response_data["data"], message="Request Submitted Successful")
            elif response.status_code == 404:
                response_data = response.json()
                return Response(status=True, code=ResponseCode.NO_RECORD_FOUND,
                                data=None, message=response_data["message"])
            else:
                return Response(status=True, code=ResponseCode.NO_RECORD_FOUND,
                                data=None, message=response_data["message"])
        else:
            response_data = response.json()
            return Response(status=True, code=ResponseCode.NO_RECORD_FOUND,
                            data=None, message=response_data["message"])
