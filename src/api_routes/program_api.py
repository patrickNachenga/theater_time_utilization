from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from src.modules.programs.service import ProgramService
from src.types import ProgramCodeInput

program_router = APIRouter()
root_path = "/program"


# @program_router.get(root_path)
# async def get_program_data(code: str | None = None, uid: str | None = None):
#     if code:
#         return await ProgramService.api_get_program_by_code(code=code)
#     elif uid:
#         return await ProgramService.api_get_program_by_code(uid=uid)
#     else:
#         return await ProgramService.api_get_programs()


class ProgramDepartmentInput(BaseModel):
    departments: List[str]


@program_router.get("/program")
async def get_program_data(parm: ProgramCodeInput):
    return await ProgramService.api_get_program_by_code(parm)


@program_router.get("/programs")
async def get_program_data():
    return await ProgramService.api_get_programs()


# These will get all programs uid by passed list of department
@program_router.post("/program/department")
async def get_program_data(parm: ProgramDepartmentInput):
    return ProgramService.api_get_program_by_departments(parm.departments)
