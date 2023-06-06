from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from src.modules.programs.service import ProgramService

program_router = APIRouter()
root_path = "/program"


class ProgramCodeInput(BaseModel):
    code: str


class ProgramDepartmentInput(BaseModel):
    departments: List[str]


@program_router.get("/program")
async def get_program_data(parm: ProgramCodeInput):
    return await ProgramService.api_get_program_by_code(code=parm.code)


@program_router.get("/programs")
async def get_program_data():
    return await ProgramService.api_get_programs()


@program_router.post("/program/department")
async def get_program_data(parm: ProgramDepartmentInput):
    return ProgramService.api_get_program_by_departments(parm.departments)
