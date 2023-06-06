import requests
from fastapi import FastAPI

app = FastAPI()

@app.get("/fee-structures/{program_code}")
def get_fee_structures(program_code: str):
    fee_structure_url = f"http://197.250.34.41:4747/api/v2/fee-structures?program_code={program_code}"

    try:
        # Make a request to the fee structure endpoint
        response = requests.get(fee_structure_url)
        response.raise_for_status()

        fee_structures = response.json()["data"]
        return {
            "status": 200,
            "message": "Fee Structures retrieved",
            "errors": None,
            "data": fee_structures
        }
    except requests.exceptions.RequestException as e:
        return {"message": "Failed to retrieve fee structures", "errors": str(e)}
