import json
from typing import Optional, List

import requests
from fastapi.encoders import jsonable_encoder
from requests import options
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload

from src.core.config import settings
from src.db.session import session_scope
from src.models import ProgramCourse, Program, AcademicYear, StudentProgramChange, Workflow, TransitionMeta, Process, \
    ProcessFlow, State
from src.modules import CRUDBase
from src.modules.academic_year.service import AcademicYearService
from src.modules.programs.service import ProgramService
from src.modules.states.service import StateService
from src.modules.transition_metas.service import TransitionMetaService
from src.modules.workflows.service import WorkflowService
from src.shared.models import StudentModel
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCourseListNode, StudentProgramChangeInput, StudentProgramChangeNode


class StudentProgramChangeService(CRUDBase[StudentProgramChange, StudentProgramChangeInput, StudentProgramChangeInput]):
    @staticmethod
    def get_all_student_change_programs() -> List[StudentProgramChange]:
        """
        Get Student Program Change off all student
        :param:
        :return StudentProgramChange:
        """
        with session_scope() as session:
            student_program_changes = session.query(StudentProgramChange).order_by(
                desc(StudentProgramChange.updated_at)).all()
            if student_program_changes:
                students_uids = [str(student_program_change.student_uid) for student_program_change in
                                 student_program_changes]
                # students_uids = [
                #     "5a8c0931-a61f-4bc5-b9ff-5050cc789337", "cd5e690d-6e16-4fa0-8c0c-b0e02138de86"
                # ]
                if students_uids:
                    # go to uaa to get student information
                    data_obj = {
                        "uids": students_uids
                    }
                    # Serialize the data to JSON
                    payload = json.dumps(data_obj)
                    # Set the Content-Type header to indicate that the request body is JSON
                    headers = {
                        "Content-Type": "application/json"
                    }
                    # Send the Get request
                    response = requests.post(settings.UAA_URi + f'/students-details-by-uids', data=payload,
                                             headers=headers)
                    response.raise_for_status()
                    # print(response.json())
                    if response.status_code == 200:
                        response_data = response.json()
                        print(response_data)
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
                # Verify and get supplied Program uid to get existed program model
                academic_year = AcademicYearService(AcademicYear).get_active_academic_year()
                if academic_year is None:
                    return Response(
                        status=False,
                        code=ResponseCode.BAD_REQUEST,
                        data=None,
                        message="Academic year Does not exist"
                    )
                # get student
                params = {"uid": input.student_uid}
                response = requests.get(settings.UAA_URi + f'/users/student', params=params)
                if response.status_code == 200:
                    result = response.json()
                    if result:
                        student = StudentModel(**result)
                        current_program_uid = student.programme_uid
                        current_registration_number = student.registration_number

                        # Check if this is the same program
                        if input.new_program_uid == current_program_uid:
                            return Response(
                                status=False,
                                code=ResponseCode.BAD_REQUEST,
                                data=None,
                                message="You Cant Request For the Same Program"
                            )
                        # Check if There Are Pending Request for this User
                        existed_request = session.query(StudentProgramChange).filter(
                            (StudentProgramChange.approve_status == "PENDING"),
                            (StudentProgramChange.student_uid == input.student_uid)
                        ).first()

                        if existed_request:
                            return Response(
                                status=False,
                                code=ResponseCode.BAD_REQUEST,
                                data=None,
                                message="Your already have Program change request on Go"
                            )

                        # Verify and get supplied Current Program uid to get existed program model
                        current_program = ProgramService(Program).get(current_program_uid)
                        if current_program is None:
                            return Response(
                                status=False,
                                code=ResponseCode.FAILURE,
                                data=None,
                                message="Failed to get Current Student Program"
                            )

                        # Verify and get supplied Program uid to get existed program model
                        new_program = ProgramService(Program).get(input.new_program_uid)
                        if new_program is None:
                            return Response(
                                status=False,
                                code=ResponseCode.BAD_REQUEST,
                                data=None,
                                message="You have submitted incorrect new program details"
                            )

                        workflow = WorkflowService(Workflow).get_workflow_by_name('PROGRAM_CHANGE')
                        if workflow is None:
                            return Response(
                                status=False,
                                code=ResponseCode.BAD_REQUEST,
                                data=None,
                                message="Program Change Workflow Does not exist"
                            )

                        if input.uid is None:
                            state = StateService(State).get_state_by_label('Requested')
                            if state is None:
                                return Response(
                                    status=False,
                                    code=ResponseCode.BAD_REQUEST,
                                    data=None,
                                    message="State Workflow 'Requested' Does not exist"
                                )

                            student_program_change = StudentProgramChange(
                                student_uid=input.student_uid,
                                academic_year_id=academic_year.id,
                                current_program_id=current_program.id,
                                new_program_id=new_program.id,
                                reason=input.reason,
                                approve_status=state.label,
                                approve_remark="",
                                current_registration_number=current_registration_number
                            )

                            local_object = session.merge(student_program_change)
                            session.add(local_object)
                            session.commit()
                            process = session.query(Process).filter(
                                Process.process_unique_uid == student_program_change.uid).first()
                            if process is None:
                                process = Process(description='PROGRAM_CHANGE',
                                                  process_unique_uid=student_program_change.uid,
                                                  workflow_id=workflow.id)
                                session.add(process)
                                session.commit()
                            # Change state process
                            process_flow = ProcessFlow(state_id=state.id, process_id=process.id)
                            session.add(process_flow)
                            session.commit()

                            student_program_change = self.get(local_object.uid)
                            return Response(status=True, code=ResponseCode.SUCCESS,
                                            data=student_program_change,
                                            message=f"Your Request Submitted Successfully")
                        else:
                            student_program_change = self.get(input.uid)
                            if student_program_change:
                                obj_data = jsonable_encoder(input)
                                # # Replace referenced uids field with model required ids field
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

                    else:
                        return Response(
                            status=False,
                            code=ResponseCode.NO_RECORD_FOUND,
                            data=None,
                            message="Student Supplied does not exists"
                        )
                else:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=None,
                        message="Failed to retrieve Student Detail"
                    )

            except Exception as e:
                print(e)
                return Response(status=False, code=ResponseCode.FAILURE,
                                data=None,
                                message=f"Your Request is Unsuccessful")


ProgramCourseCrud = StudentProgramChangeService(StudentProgramChange)
