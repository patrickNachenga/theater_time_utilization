from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from src.modules.programs.service import ProgramService

program_router = APIRouter()
root_path = "/program"

<<<<<<< HEAD
@program_router.get(root_path)
async def get_program_data(code: str | None = None):
    if code:
        return await ProgramService.api_get_program_by_code(code=code)
    else:
        return await ProgramService.api_get_programs()

=======
>>>>>>> f6c1bcacea4d7921ee708b1416f5cbbc1e42806d

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
<<<<<<< HEAD
    return await ProgramService.api_get_program_by_departments(parm.departments)

=======
    return ProgramService.api_get_program_by_departments(parm.departments)
>>>>>>> f6c1bcacea4d7921ee708b1416f5cbbc1e42806d
