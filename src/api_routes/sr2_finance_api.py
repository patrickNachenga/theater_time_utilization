from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from src.modules.programs.service import ProgramService
from src.modules.sr2_api_calls.service import Sr2ApiCalls
from src.types import ControlNumberInput

sr2_router = APIRouter()
root_path = "/control_number"


# These will get all programs uid by passed list of department
@sr2_router.post(f"{root_path}/save")
async def register_control_number(parm: ControlNumberInput):
    return Sr2ApiCalls.register_control_numbers(parm)


