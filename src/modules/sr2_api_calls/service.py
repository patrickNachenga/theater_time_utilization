from typing import List
from urllib.parse import urlencode

import requests

from src.db.session import session_scope
from src.models import Program
from src.models.fee_structure import FeeStructure
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import FeeStructureInput, FeeStructureNode, ControlNumberInput, ControlNumberNode


class Sr2ApiCalls(object):
    token = '9454c6efdb94236e618c9a7b1a67138b'
    site_url = 'http://197.250.34.41:4747/api/v2/'

    @staticmethod
    def request_fee_structure(inputs: FeeStructureInput) -> Response[List[FeeStructureNode]] | None:

        # Verify and get supplied Program code and exists
        with session_scope() as session:
            program = session.query(Program).filter_by(code=inputs.program_code).first()
            if not program:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None, message="Program Not Found")
            # Check if the program code already exists in the fee structure table
            existing_fee_structure = session.query(FeeStructure).filter_by(program=program).first()

            if not existing_fee_structure:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None, message="Fee structure for %s was Not Found" % program.code)
            # Set the request payload
            payload = {
                "program_code": inputs.program_code,
                "year_of_study": inputs.year_of_study,
                "study_level": inputs.study_level,
                "student_status": inputs.student_status,
                "countrycode": inputs.countrycode,
            }
            encoded_params = urlencode(payload)
            # Send the Get request
            response = requests.get(Sr2ApiCalls.site_url + f"billing/program_fee_structure?{encoded_params}")

            # Check for errors
            if response.status_code == 200:
                response_data = response.json()
                fee_structure = []
                for structure in response_data["data"]:
                    fee_structure.append(
                        FeeStructure(
                            name=structure["fee_name"],
                            amount=float(structure["amount"]),
                            study_year=inputs.year_of_study,
                            min_amount=float(structure["min_amount"]),
                            currency=structure["currency"],
                            program=program
                        )
                    )
                session.add_all(fee_structure)
                session.commit()
                return Response(status=True, code=ResponseCode.SUCCESS,
                                data=fee_structure, message="Fee Successfully Retrieved")
            else:
                print(response)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to retrieve fee structure",
                    data=None)

    @staticmethod
    def request_control_numbers(inputs: ControlNumberInput) -> Response[List[ControlNumberNode]] | None:

        # Verify and get supplied Program code and exists
        with session_scope() as session:
            '''
            program = session.query(Program).filter_by(code=inputs.program_code).first()
            if not program:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None, message="Program Not Found")
            
            # Check if the program code already exists in the fee structure table
            existing_fee_structure = session.query(FeeStructure).filter_by(program=program).first()

            if not existing_fee_structure:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=None, message="Fee structure for %s was Not Found" % program.code)
            '''
            # Set the request payload
            payload = {

                "program_code": inputs.program_code,
                "year_of_study": inputs.year_of_study,
                "study_level": inputs.study_level,
                "student_status": inputs.student_status,
                "countrycode": inputs.countrycode,
                "registration_number": inputs.registration_number,
                "program_name": inputs.program_name,
                "system": inputs.system,
            }

            encoded_params = urlencode(payload)

            # Send the Get request
            response = requests.post(Sr2ApiCalls.site_url + f"billing/program_fee_structure",data=payload)

            # Check for errors
            if response.status_code == 200:
                response_data = response.json()
                print("__________________________")
                control_number_info = []
                for control_number_item in response_data["data"]:
                    control_number_info.append(control_number_item)
                print("+++++++++++++++++++++++++++++++++++++++++++++")
                print(control_number_info)
                return Response(status=True, code=ResponseCode.SUCCESS,
                                data=None, message="Control number request generated successfully")
            else:
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to generate control number request",
                    data=None)
