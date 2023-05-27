from fastapi import APIRouter

from src.modules.programs.service import ProgramService

router = APIRouter()


@router.get("/program")
async def get_program_data(code: str | None = None):
    return await ProgramService().api_get_program_by_code(code=code)
