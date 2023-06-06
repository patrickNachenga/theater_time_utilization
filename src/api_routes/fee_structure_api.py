# import requests
# from fastapi import FastAPI
# from src.db.session import session_scope
# from src.models.program import Program
#
# app = FastAPI()
#
# @app.get("/fee-structures/{program_code}")
# def get_fee_structures(program_code: str):
#     fee_structure_url = f"http://197.250.34.41:4747/api/v2/fee-structures?program_code={program_code}"
#
#     try:
#         # Check if the program code exists in the program table
#         with session_scope() as session:
#             program = session.query(Program).filter(Program.code == program_code).first()
#             if program is None:
#                 return {"message": "Program code not found", "errors": None}
#
#         # Make a request to the fee structure endpoint
#         response = requests.get(fee_structure_url)
#         response.raise_for_status()
#
#         fee_structures = response.json()["data"]
#
#         # Add program UID and program category to each fee structure
#         for fee_structure in fee_structures:
#             fee_structure["program_uid"] = program.program_uid
#             fee_structure["program_category"] = program.program_category
#
#         return {
#             "status": 200,
#             "message": "Fee Structures retrieved",
#             "errors": None,
#             "data": fee_structures
#         }
#     except requests.exceptions.RequestException as e:
#         return {"message": "Failed to retrieve fee structures", "errors": str(e)}
#
#
