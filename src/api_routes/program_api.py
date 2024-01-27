import io
from io import BytesIO
from typing import List

import openpyxl
from fastapi import APIRouter, UploadFile, File
from openpyxl.styles import Alignment, Font, Border, Side, Protection
from pydantic import BaseModel

from src.db.session import session_scope
from src.helpers.utils import insert_exam_result, insert_course_work, get_student_from_uaa
from src.models import ExamCategory
from src.modules.academic_year.service import AcademicYearCrud
from src.modules.by_law.by_law_classes import BYLAW
from src.modules.by_law.by_law_files.by_law_2019 import ByLaw2019
from src.modules.by_law.service import ByLawCrud
from src.modules.programs.service import ProgramService
from src.modules.semester_registration.service import SemesterRegistrationService
from src.modules.student.service import StudentService
from src.shared.models import StudentPChangeModel
from src.shared.response import Response
from src.shared.response_code import ResponseCode

program_router = APIRouter()
root_path = "/program"

from starlette.responses import StreamingResponse
from openpyxl import Workbook


@program_router.get(root_path)
async def get_program_data(code: str | None = None, uid: str | None = None):
    if code:
        return await ProgramService.api_get_program_by(code=code)
    elif uid:
        return await ProgramService.api_get_program_by(uid=uid)
    else:
        return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                        message="Program Not Found", data=None)


class ProgramDepartmentInput(BaseModel):
    departments: List[str]


# class StudentPChangeInput(BaseModel):
#     students: List[str]


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


@program_router.get("/active-by-law")
def get_active_by_law():
    try:
        result = ByLawCrud.get_active_by_law()
    except Exception as e:
        print(e)
        result = None
    return result


@program_router.get("/active-academic-year")
def get_active_by_academic_year():
    try:
        result = AcademicYearCrud.get_active_academic_year()
    except Exception as e:
        print(e)
        result = None
    return result


@program_router.get("/program-for-nhif")
async def api_get_program_name_duration(uid: str):
    return await ProgramService.api_get_program_name_duration(uid)


@program_router.get('/get-semester-registered-students')
def get_semester_registered_students():
    try:
        student_uids = SemesterRegistrationService.get_active_year_student_semester_registrations()
        if student_uids:
            return Response(status=True, code=ResponseCode.SUCCESS,
                            message="Success", data=student_uids)
    except Exception as e:
        print(e)
    return Response(status=False, code=ResponseCode.NO_RECORD_FOUND, message="No Record", data=[])


@program_router.get("/program-change-students")
async def api_get_program_change_student_list():
    return await ProgramService.api_get_program_change_student_list()


@program_router.post("/get-uqf-pchanges")
async def api_get_uqf_pchanges_list(parm: StudentPChangeModel):
    return await ProgramService.api_get_uqf_pchanges_list(parm)


@program_router.post("/generate-allocation-template/")
def generate_allocation_xls_template(allocation_uid: str, out_off: int, exam_category: int, assessment_number: int,
                                     assessment_weight: int):
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
    vertical_headers = ["Course Ante", "Program Code", "Academic Year", "Study Year", "Exam Category", "Assessment No",
                        "Mark Out of",
                        "Assessment Weight"]
    # Sample data for the vertical header
    data = {
        "Course Ante": result["program_course"].course.code,
        "Program Code": result["program_course"].program_semester.program.code,
        "Academic Year": result["program_course"].program_semester.academic_year.name,
        "Study Year": str(result["program_course"].program_semester.study_year),
        "Exam Category": str(exam_category),
        "Assessment No": str(assessment_number),
        "Mark Out of": str(out_off),
        "Assessment Weight": str(assessment_weight)
    }
    worksheet.sheet_view.showGridLines = False
    # Generate the data for the vertical header
    vertical_data = [data[header] for header in vertical_headers]
    for row, header in enumerate(vertical_headers, start=1):
        cell = worksheet.cell(row=row, column=1, value=header)
        cell.alignment = Alignment(horizontal='left')
        cell.font = font_border
        cell.border = None
        cell.protection = Protection(locked=False)
    for row, value in enumerate(vertical_data, start=1):
        cell = worksheet[f"C{row}"]
        cell.value = value
        cell.font = font_border
        cell.border = None
        cell.protection = Protection(locked=False)
    # Define the horizontal headers
    # worksheet.sheet_view.showGridLines = True
    horizontal_headers = ["SN", "Reg No", "Name", "Marks"]
    start_col = 1  # Start column for horizontal headers
    start_row = len(vertical_headers) + 1  # Start row for horizontal headers

    for col, header in enumerate(horizontal_headers, start=start_col):
        cell = worksheet.cell(row=start_row, column=col, value=header)
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.font = font_border
        cell.border = border

    count = 0
    print('data ===>', result['data'])
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
    worksheet.cell(row=1, column=4, value=str(result["program_course"].id))
    # Set the specific column where cells should be non-editable (except column D)
    editable_column = 'D'

    # Iterate over rows in the worksheet
    for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column):
        for cell in row:
            # Check if the current column is the editable column and cell row is not greater than 9
            if cell.column_letter == editable_column and cell.row >= 10:
                # Set protection to False for the editable column
                cell.protection = Protection(locked=False)
                cell.number_format = '0.00'
                # if cell.value is not None and float(int(cell.value)) > out_off:
                #     cell.value = 0  # Set the value to 10 if it's greater than 10
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
    exam_category_id = worksheet.cell(row=5, column=3).value
    assessment_number = worksheet.cell(row=6, column=3).value
    out_off = float(worksheet.cell(row=7, column=3).value)
    program_course_id = worksheet.cell(row=1, column=4).value
    weight = float(worksheet.cell(row=8, column=3).value)

    # Assuming the data is in a specific sheet and columns
    sn_column = 1  # Assuming SN is in column A
    reg_no_column = 2  # Assuming Reg No is in column B
    name_column = 3  # Assuming Name is in column C
    marks_column = 4  # Assuming Marks is in column D

    with session_scope() as session:
        is_ue = session.query(ExamCategory).filter(
            ExamCategory.id == exam_category_id).first().exam_category_group.is_ue
        # get student list from uaa service to get student uid after filtering
        students = get_student_from_uaa()
        success = 0
        failed = 0
        failed_students = []
        response_data = {
            "success": 0,
            "failed": 0,
            "failed_students": []
        }
        for row in worksheet.iter_rows(min_row=10, values_only=True):
            reg_number = row[reg_no_column - 1]
            score = float(row[marks_column - 1])
            # Find the item with the specified registration_number
            if students:
                matching_item = next(
                    (item for item in students if item["registration_number"] == reg_number), None)
                if matching_item:
                    student_uid = matching_item["uid"]
                    # print('student',reg_number,student_uid)
                    if score <= out_off:
                        if is_ue:
                            result = insert_exam_result(student_uid, program_course_id, exam_category_id, score,
                                                        out_off,
                                                        weight)
                            if result:
                                success = success + 1
                            else:
                                failed = failed + 1
                                failed_students.append({"reg_number": reg_number, "reason": "Data processing error"})
                        else:
                            result = insert_course_work(student_uid, program_course_id, exam_category_id,
                                                        assessment_number,
                                                        out_off, score,
                                                        weight)
                            if result:
                                if result:
                                    success = success + 1
                                else:
                                    failed = failed + 1
                                    failed_students.append(
                                        {"reg_number": reg_number, "reason": "Data processing error"})

                    else:
                        failed = failed + 1
                        failed_students.append({"reg_number": reg_number, "reason": "Score is greater than out off"})
                else:
                    failed = failed + 1
                    failed_students.append(
                        {"reg_number": reg_number, "reason": "Data processing error ,student not found"})

            else:
                failed = failed + 1
                failed_students.append(
                    {"reg_number": reg_number, "reason": "Data processing error , UAA service not found"})

    # Save the extracted data in the database
    # ...
    response_data["failed_students"] = failed_students
    response_data["failed"] = failed
    response_data["success"] = success
    return response_data
