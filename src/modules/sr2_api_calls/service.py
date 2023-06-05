from typing import Any

import requests

from src.models import Program
from src.modules.programs.service import ProgramService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramFeeStructureInput


class Sr2ApiCalls(object):
    token = '9454c6efdb94236e618c9a7b1a67138b'
    site_url = 'http://10.2.1.165/sr2/rest/server.php'

    @staticmethod
    async def request_fee_structure(inputs: ProgramFeeStructureInput) -> Response[Any]:
        try:
            # Verify and get supplied Program uid and get existed program model
            program = ProgramService(Program).get_program_by_code(inputs.code)
            if program is None:
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    data=None,
                    message="You have submitted incorrect program details"
                )

            # Set the request payload
            payload = {
                'token': Sr2ApiCalls.token,
                'function': 'core_user_create_users',
                'format': 'json',
                'data[0][code]': inputs.code,
                'data[0][study_year]': inputs.study_year,
            }
            # Send the Get request
            response = requests.get(Sr2ApiCalls.site_url, data=payload)
            # Check for errors
            if response.status_code == 200:
                response_data = response.json()
                print(response_data)
                return response_data
            else:
                print('HTTP Error:', response.status_code)
                # Decode the response
                return None
        except Exception as e:
            print(e)
            return None
