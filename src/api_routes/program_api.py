from fastapi import APIRouter

from src.modules.programs.service import ProgramService

program_router = APIRouter()
root_path = "/program"


@program_router.get(root_path)
async def get_program_data(code: str | None = None):
    if code:
        return await ProgramService.api_get_program_by_code(code=code)
    else:
        return await ProgramService.api_get_programs()
