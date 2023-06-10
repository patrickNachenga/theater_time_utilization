from typing import List, Optional
from urllib.parse import urlencode

import requests
from sqlalchemy import desc, select

from src.db.session import session_scope
from src.models import Program
from src.models.control_number import ControlNumber
from src.models.fee_structure import FeeStructure
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import FeeStructureInput, RequestControlNumberInput, ControlNumberNode, ControlNumberInput
from src.types import FeeStructureNode, RequestControlNumberNode


class Sr2ApiCalls(object):
    token = '9454c6efdb94236e618c9a7b1a67138b'
    site_url = 'http://197.250.34.41:4747/api/v2/'

    @staticmethod
    def request_fee_structure(inputs: FeeStructureInput) -> Response[List[FeeStructureNode]] | None:
        """
        This is a function to request program fee structure  from SR2
        """
        # Verify and get supplied Program code and exists
        with session_scope() as session:
            program = session.query(Program).filter_by(uid=inputs.program_uid).first()
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
                "program_code": program.code,
                "year_of_study": inputs.year_of_study,
                "study_level": program.program_category.code,
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
                "system": inputs.system,
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
    def register_control_numbers(input: ControlNumberInput) -> Response[Optional[str]]:
        """
       Register control number to db generated form sr2
       :param input:
       :return Optional[str]:
       """
        with session_scope() as session:
            try:
                control_number = ControlNumber(
                    registration_number=input.registration_number,
                    bill_id=input.billid,
                    fee_name=input.fee_name,
                    amount=input.amount,
                    control_number=input.control_number,
                    currency=input.currency,
                    pay_type=input.pay_type,
                    academic_year=input.academic_year,
                )
                session.add(control_number)
                session.commit()
                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Control number registered successful",
                    data=None)
            except Exception as e:
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    message="Failed to register control number",
                    data=None)

    @staticmethod
    def get_student_control_number(registration_number: str) -> List[ControlNumberNode] | None:
        """
       Get Student saved control number
       :param registration_number:
       :return Optional[str]:
       """
        with session_scope() as session:
            try:
                stmt = select(ControlNumber).where((ControlNumber.registration_number == registration_number) & (ControlNumber.deleted_at.is_(None)))
                result = session.scalars(stmt)
                return result.all()
            except Exception as e:
                print(e)
                return None
