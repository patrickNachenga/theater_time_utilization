from typing import Optional, List

import requests
from fastapi.encoders import jsonable_encoder
from requests import options
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload

from src.core.config import settings
from src.db.session import session_scope
from src.models import ProgramCourse, Program, AcademicYear, StudentProgramChange
from src.modules import CRUDBase
from src.modules.academic_year.service import AcademicYearService
from src.modules.programs.service import ProgramService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCourseListNode, StudentProgramChangeInput, StudentProgramChangeNode


class StudentProgramChangeService(CRUDBase[StudentProgramChange, StudentProgramChangeInput, StudentProgramChangeInput]):
    @staticmethod
    def get_all_student_change_programs() -> List[StudentProgramChange]:
        """
        Get Student Program Change off all student
        :param uid:
        :return StudentProgramChange:
        """
        with session_scope() as session:
            student_program_changes = session.query(StudentProgramChange).filter(
                StudentProgramChange.deleted_at.is_(None)).order_by(desc(StudentProgramChange.updated_at)).all()
            if student_program_changes:
                students_uids = [student_program_change.uid for student_program_change in student_program_changes]
                params = {"uids": students_uids}
                response = requests.get(settings.UAA_URi + f'/students-details-by-uids', params=params)
                response.raise_for_status()
                if response.status_code == 200:
                    responseData = response.json()
                    print(responseData)
            return student_program_changes

    @staticmethod
    def get_student_change_programs(uid: str) -> List[StudentProgramChange]:
        """
        Get all Student Program Change
        :param uid:
        :return StudentProgramChange:
        """
        with session_scope() as session:
            result = session.query(StudentProgramChange).filter((StudentProgramChange.student_uid == uid),
                                                                StudentProgramChange.deleted_at.is_(None)).order_by(
                desc(StudentProgramChange.updated_at)).all()
            return result

    @staticmethod
    def get_student_change_program_by_uid(uid: str) -> StudentProgramChange:
        """
        Get Student Program Change  by uid
        :param uid:
        :return StudentProgramChange:
        """
        with session_scope() as session:
            stmt = select(StudentProgramChange).where(
                (StudentProgramChange.uid == uid) & (StudentProgramChange.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def student_change_program(self, input: StudentProgramChangeInput) -> Response[StudentProgramChangeNode]:
        """
        Register Student Program Change
        :param input:
        :return Response[Optional[StudentProgramChangeNode]]:
        """
        with session_scope() as session:
            try:
                # Check if this is the same program
                if input.new_program_uid == input.current_program_uid:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=None,
                        message="You Cant Request For the Same Program"
                    )

                # Check if There Are Pending Request for this User
                existed_request = session.query(StudentProgramChange).filter(
                    (StudentProgramChange.approve_status == "PENDING"),
                    (StudentProgramChange.student_uid == input.student_uid),
                    (StudentProgramChange.deleted_at.is_(None)),
                ).first()
                if existed_request:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=None,
                        message="Your already have Program change request on Go"
                    )

                # Verify and get supplied Current Program uid to get existed program model
                current_program = ProgramService(Program).get_program_by_uid(input.current_program_uid)
                if current_program is None:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=None,
                        message="You have submitted incorrect current program details"
                    )

                # Verify and get supplied Program uid to get existed program model
                new_program = ProgramService(Program).get_program_by_uid(input.new_program_uid)
                if new_program is None:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=None,
                        message="You have submitted incorrect new program details"
                    )
                # Verify and get supplied Program uid to get existed program model
                academic_year = AcademicYearService(AcademicYear).get_active_academic_year()
                if academic_year is None:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=None,
                        message="Academic year Does not exist"
                    )

                if input.uid is None:
                    student_program_change = StudentProgramChange(
                        student_uid=input.student_uid,
                        academic_year_id=academic_year.id,
                        current_program=current_program,
                        new_program=new_program,
                        reason=input.reason,
                        approve_status="PENDING",
                        approve_remark="",
                        current_registration_number=input.current_registration_number
                    )
                    local_object = session.merge(student_program_change)
                    session.add(local_object)
                    session.commit()
                    student_program_change = self.get_student_change_program_by_uid(local_object.uid)
                    return Response(status=True, code=ResponseCode.SUCCESS,
                                    data=student_program_change,
                                    message=f"Your Request Submitted Successful")
                else:
                    student_program_change = self.get_student_change_program_by_uid(input.uid)
                    if student_program_change:
                        obj_data = jsonable_encoder(input)
                        # # Replace referenced uids field with model required ids field
                        obj_data['current_program'] = current_program
                        obj_data['new_program'] = new_program
                        obj_data['academic_year'] = academic_year
                        for key, value in obj_data.items():
                            setattr(student_program_change, key, value)

                        local_object = session.merge(student_program_change)
                        session.add(local_object)
                        session.commit()
                        return Response(status=True, code=ResponseCode.SUCCESS,
                                        data=local_object,
                                        message=f"Your Request Submitted Successful")
                    else:
                        return Response(status=False, code=ResponseCode.NO_DATA_CHANGED,
                                        data=None,
                                        message=f"Your Request is Unsuccessful")
            except Exception as e:
                print(e)
                return Response(status=False, code=ResponseCode.FAILURE,
                                data=None,
                                message=f"Your Request is Unsuccessful")


ProgramCourseCrud = StudentProgramChangeService(StudentProgramChange)
