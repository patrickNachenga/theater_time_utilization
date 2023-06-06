import json
from typing import Any, List

import requests

from src.models import Program
from src.modules.programs.service import ProgramService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import FeeStructureInput, FeeStructureNode


class Sr2ApiCalls(object):
    token = '9454c6efdb94236e618c9a7b1a67138b'
    site_url = 'http://197.250.34.41:4747/api/v2/'

    @staticmethod
    def request_fee_structure(inputs: FeeStructureInput) -> List[FeeStructureNode] | None:
        try:
            # Verify and get supplied Program uid and get existed program model
            # program = ProgramService(Program).get_program_by_code(inputs.program_code)
            # if program is None:
            #     return None
            # Set the request payload
            payload = {
                "program_code": inputs.program_code,
                "year_of_study": inputs.year_of_study,
                "study_level": inputs.study_level,
                "student_status": inputs.student_status,
                "countrycode": inputs.countrycode,
            }

            print(payload)
            # Send the Get request
            response = requests.get(Sr2ApiCalls.site_url + "billing/program_fee_structure", data=payload)

            # Check for errors
            print(response.status_code)
            print("-------------------------------------------->", response.request.__dict__)
            response_data = response.json()
            print("-------------------------------------------->", response_data)
            if response.status_code == 200:
                response_data = response.json()
                # Process the response data as required
                print("-------------------------------------------->", response_data["status"])
                return []  # Return the processed data
            else:
                print('HTTP Error:', response)
                return []  # Return an empty list or handle the error condition accordingly

        except Exception as e:
            print(e)
            return []
