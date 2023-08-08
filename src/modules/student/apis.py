import base64
import io
from typing import List, Optional
from openpyxl.styles import Alignment, Font, Border, Side, Protection
from io import BytesIO

import strawberry
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

from src.core.security import CustomPermissionExtension
from src.helpers.utils import get_current_academic_year
from src.modules.student.service import StudentService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseRegistrationListNode, \
    CourseRegistrationInputNode, UaaDataResponse, StudentUaaData, ExcelFile, ProgramCourseListNode, \
    CourseRegisterInputNode, StudentProgramCourseListNode, ExamRegistrationInput, ExamRegistrationListNode, \
    ExamToRegister


@strawberry.type
class StudentQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_STUDENT_COURSE_REGISTRATIONS"])])
    def get_student_course_to_register(self, inputs: CourseRegisterInputNode) -> Response[
        Optional[StudentProgramCourseListNode]]:
        try:
            result = StudentService().get_student_course_to_register(inputs)

            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program courses Retrieved successfully",
                data=result)
        except Exception as e:
            print(e)
            result = [CourseRegistrationListNode(course_to_register=None, total_count=0, course_registered=None)]
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Program courses not found",
                data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_STUDENT_COURSE_REGISTRATIONS"])])
    def get_student_current_course_registration(self, student_uid: str) -> Response[
        Optional[CourseRegistrationListNode]]:
        try:
            result = StudentService().get_student_current_course_registration(student_uid)

            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Course Registration Retrieved successfully",
                data=result)
        except Exception as e:
            print(e)
            result = CourseRegistrationListNode(items=[], total_count=0)
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Course Registration not found",
                data=result)

    @strawberry.field()
    def get_allocation_students(self, allocation_uid: str) -> UaaDataResponse | None:
        try:
            result = StudentService().get_allocation_students(allocation_uid)

            if result:
                response = UaaDataResponse(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Successfully Retrieved",
                    data=[StudentUaaData(registration_number=item['registration_number'], full_name=item['full_name'])
                          for item in result['data']]
                )

                return response
            else:
                return UaaDataResponse(
                    status=False,
                    code=ResponseCode.NO_RECORD_FOUND,
                    message="Failed to retrieve",
                    data=[])
        except Exception as e:
            print(e)
            return UaaDataResponse(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Failed to retrieve",
                data=[])

    @strawberry.field
    def get_student_current_registered_exam(self, student_uid: str) -> Response[ExamRegistrationListNode]:
        try:
            result = StudentService().get_student_current_registered_exam(student_uid)
            if result:
                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Exam Registration Retrieved successfully",
                    data=ExamRegistrationListNode(items=result, total_count=len(result)))
            else:
                return Response(
                    status=False,
                    code=ResponseCode.NO_RECORD_FOUND,
                    message="Exam Registration not found",
                    data=ExamRegistrationListNode(items=[], total_count=0))
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Exam Registration not found",
                data=ExamRegistrationListNode(items=[], total_count=0))

    @strawberry.field
    def get_student_exam_to_register(self, student_uid: str) -> Response[ExamToRegister]:
        try:
            result = StudentService().get_student_exam_to_register(student_uid)
            if result:
                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Exam Registration Retrieved successfully",
                    data=result)
            else:
                return Response(
                    status=False,
                    code=ResponseCode.NO_RECORD_FOUND,
                    message="Exams not found",
                    data=[])
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Exams not found",
                data=[])


@strawberry.type
class StudentMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_STUDENT_COURSES"])])
    def register_student_course(self, inputs: List[CourseRegistrationInputNode],remove: List[str]) -> Response[
        CourseRegistrationListNode]:
        try:
            result = StudentService().register_student_course(inputs, remove)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Course Registered successfully",
                data=result)
        except Exception as e:
            print(e)
            result = CourseRegistrationListNode(items=[], total_count=0)
        return Response(status=False, code=ResponseCode.FAILURE, message="Failed to register course", data=result)

    @strawberry.field
    def generate_allocation_xls_template(self, allocation_uid: str, out_off: int, exam_category: int,
                                         assessment_number: int, assessment_weight: int) -> ExcelFile:
        result = StudentService().get_allocation_students(allocation_uid)
        file_buffer = io.BytesIO()

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
        vertical_headers = ["Program Code", "Academic Year", "Study Year", "Exam Category", "Assessment No",
                            "Mark Out of",
                            "Assessment Weight"]
        # Sample data for the vertical header
        data = {
            "Program Code": result["program_course"].course.code,
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
        for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=1,
                                       max_col=worksheet.max_column):
            for cell in row:
                # Check if the current column is the editable column
                if cell.column_letter == editable_column:
                    # Set protection to False for the editable column
                    cell.protection = Protection(locked=False)
                else:
                    # Set protection to True for other columns
                    cell.protection = Protection(locked=True)

        # Save the workbook
        # workbook.save("layout.xlsx")

        # Save the workbook to a BytesIO buffer
        file_buffer = BytesIO()
        workbook.save(file_buffer)
        file_buffer.seek(0)

        # Convert the Excel file to Base64 string
        file_data = file_buffer.getvalue()
        base64_data = base64.b64encode(file_data).decode()

        # Return the Base64 string as the result
        return ExcelFile(base64_data=base64_data)

    @strawberry.field
    def register_student_exam(self, inputs: ExamRegistrationInput) -> Response[ExamRegistrationListNode]:
        try:
            result = StudentService().register_student_exam(inputs)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Exam Registered successfully",
                data=result)
        except Exception as e:
            print(e)
            result = ExamRegistrationListNode(items=[], total_count=0)
        return Response(status=False, code=ResponseCode.FAILURE, message="Failed to register exam", data=result)
