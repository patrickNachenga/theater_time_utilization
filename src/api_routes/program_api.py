
from io import BytesIO
from typing import List

from typing import List, Optional


from fastapi import APIRouter
from openpyxl.styles import Alignment, Font, Border, Side
from pydantic import BaseModel

from src.modules.programs.service import ProgramService

from src.modules.student.service import StudentService

from src.types import ProgramCodeInput


program_router = APIRouter()
root_path = "/program"

from starlette.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.utils import get_column_letter


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



@program_router.get("/generate-allocation-template/{allocation_uid}")
def generate_allocation_xls_template(allocation_uid: str):
    result = StudentService().get_allocation_students(allocation_uid)
    # Create a new workbook
    workbook = Workbook()

    # Create a new worksheet
    worksheet = workbook.active
    # Set column widths
    worksheet.column_dimensions['A'].width = 15
    worksheet.column_dimensions['B'].width = 20
    worksheet.column_dimensions['C'].width = 45

    # Set the font style to Times New Roman
    font = Font(name="Times New Roman")
    font_border = Font(name="Times New Roman", bold=True)
    # Set the border style
    border = Border(left=Side(border_style="thin"),
                    right=Side(border_style="thin"),
                    top=Side(border_style="thin"),
                    bottom=Side(border_style="thin"))

    # Define the vertical headers
    vertical_headers = ["Program Code", "Academic Year", "Study Year", "Exam Category", "Assessment No", "Mark Out of",
                        "Assessment Weight"]
    # Sample data for the vertical header
    data = {
        "Program Code": "FOR",
        "Academic Year": "2022/2023",
        "Study Year": "1",
        "Exam Category": "4",
        "Assessment No": "1",
        "Mark Out of": "100",
        "Assessment Weight": "1"
    }
    worksheet.sheet_view.showGridLines = False
    # Generate the data for the vertical header
    vertical_data = [data[header] for header in vertical_headers]
    for row, header in enumerate(vertical_headers, start=2):
        cell = worksheet.cell(row=row, column=1, value=header)
        cell.alignment = Alignment(horizontal='left')
        cell.font = font_border
        cell.border = None
    for row, value in enumerate(vertical_data, start=2):
        cell = worksheet[f"C{row}"]
        cell.value = value
        cell.font = font_border
        cell.border = None
    # Define the horizontal headers
    # worksheet.sheet_view.showGridLines = True
    horizontal_headers = ["SN", "Reg No", "Name", "Marks"]
    start_col = 1  # Start column for horizontal headers
    start_row = len(vertical_headers) + 2  # Start row for horizontal headers

    for col, header in enumerate(horizontal_headers, start=start_col):
        cell = worksheet.cell(row=start_row, column=col, value=header)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.font = font_border
        cell.border = border

    count = 0
    for row, item in enumerate(result['data'], start=10):
        count += 1
        worksheet[f"A{row}"] = count
        worksheet[f"B{row}"] = item['registration_number']
        worksheet[f"C{row}"] = item['full_name']
        worksheet[f"D{row}"] = ""
        # Align the cells to the center
        for col in range(1, 5):
            cell = worksheet.cell(row=row, column=col)
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.font = font
            cell.border = border

    # Save the workbook
    workbook.save("layout.xlsx")

    # Save the workbook to a BytesIO buffer
    file_buffer = BytesIO()
    workbook.save(file_buffer)
    file_buffer.seek(0)

    # Set the appropriate headers for the response
    headers = {
        "Content-Disposition": f"attachment; filename=allocation_template.xlsx",
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }

    # Return the workbook as a streaming response
    return StreamingResponse(content=file_buffer, headers=headers)

