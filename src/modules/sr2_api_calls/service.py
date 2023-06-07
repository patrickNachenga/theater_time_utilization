from typing import List, Any
from urllib.parse import urlencode

import requests

from src.db.session import session_scope
from src.models import Program
from src.models.fee_structure import FeeStructure
from src.modules.programs.service import ProgramService
from src.types import FeeStructureInput, ControlNumberInput


class Sr2ApiCalls(object):
    token = '9454c6efdb94236e618c9a7b1a67138b'
    site_url = 'http://197.250.34.41:4747/api/v2/'

    @staticmethod
    def request_fee_structure(inputs: FeeStructureInput) -> List[FeeStructure] | None:
        try:
            # Verify and get supplied Program uid and get existed program model
            with session_scope() as session:
                program = session.query(Program).filter_by(code=inputs.program_code).first()
                if program is None:
                    return None

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
                                min_amount=float(structure["min_amount"]),
                                currency=structure["currency"],
                                program=program
                            )
                        )
                    session.add_all(fee_structure)
                    session.commit()
                    return fee_structure
                else:
                    return []

        except Exception as e:
            print(e)
            return []

    @staticmethod
    def generate_control_number(inputs: ControlNumberInput) -> Any:
        try:
            # Verify and get supplied Program uid and get existed program model
            program = ProgramService(Program).get_program_by_code(inputs.program_code)
            if program is None:
                return None
            # Set the request payload
            payload = {
                "program_code": inputs.program_code,
                "year_of_study": inputs.year_of_study,
                "study_level": inputs.study_level,
                "student_status": inputs.student_status,
                "countrycode": inputs.countrycode,
                "registration_number": inputs.registration_number,
                "program_name": inputs.program_name,
                "system": inputs.system
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
                            min_amount=float(structure["min_amount"]),
                            currency=structure["currency"]
                        )
                    )
                return fee_structure
            else:
                return []

        except Exception as e:
            print(e)
            return []
