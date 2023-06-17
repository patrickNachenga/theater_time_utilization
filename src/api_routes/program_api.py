
import io
from io import BytesIO
from typing import List

import openpyxl
from fastapi import APIRouter, UploadFile, File
from openpyxl.styles import Alignment, Font, Border, Side, Protection
from pydantic import BaseModel

from src.modules.programs.service import ProgramService
from src.modules.student.service import StudentService
from src.shared.response import Response
from src.shared.response_code import ResponseCode

program_router = APIRouter()
root_path = "/program"

from starlette.responses import StreamingResponse
from openpyxl import Workbook


@program_router.get(root_path)
async def get_program_data(code: str | None = None, uid: str | None = None):
    if code:
        return await ProgramService.api_get_program_by_code(code=code)
    elif uid:
        return await ProgramService.api_get_program_by_code(uid=uid)
    else:
        return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                        message="Program Not Found", data=None)


class ProgramDepartmentInput(BaseModel):
    departments: List[str]


# @program_router.get("/program")
# async def get_program_data(parm: ProgramCodeInput):
#     print(parm)
#     return await ProgramService.api_get_program_by_code(parm)


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
        # Set the specific column where cells should be non-editable (except column D)
        editable_column = 'D'

        # Iterate over rows in the worksheet
        for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column):
            for cell in row:
                # Check if the current column is the editable column
                if cell.column_letter == editable_column:
                    # Set protection to False for the editable column
                    cell.protection = Protection(locked=False)
                else:
                    # Set protection to True for other columns
                    cell.protection = Protection(locked=True)

        # Protect the worksheet to make cells not editable
        worksheet.protection.sheet = True

    # Save the workbook
    # workbook.save("layout.xlsx")

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

@program_router.post("/extract-data")
async def extract_data(file: UploadFile = File(...)):
    contents = await file.read()

    # Load the workbook from the file contents
    workbook = openpyxl.load_workbook(io.BytesIO(contents))

    # Get the desired worksheet by name or index
    worksheet = workbook.active  # Modify this line with the appropriate worksheet name or index

    # Assuming the data is in a specific sheet and columns
    sn_column = 1  # Assuming SN is in column A
    reg_no_column = 2  # Assuming Reg No is in column B
    name_column = 3  # Assuming Name is in column C
    marks_column = 4  # Assuming Marks is in column D

    # Extract the data from the columns
    data = []
    for row in worksheet.iter_rows(min_row=10, values_only=True):
        print("SN",row[sn_column - 1])
        print("Reg No", row[reg_no_column - 1],)
        print("Marks", row[marks_column - 1])
        #
        # data.append({
        #     "sn": row[sn_column - 1],
        #     "reg_no": row[reg_no_column - 1],
        #     "name": row[name_column - 1],
        #     "marks": row[marks_column - 1]
        # })

    # Save the extracted data in the database
    # ...

    return {"message": "Data extracted successfully"}

