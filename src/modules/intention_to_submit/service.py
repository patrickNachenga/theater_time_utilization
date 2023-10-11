import json
import uuid
from typing import List

import pendulum
import requests
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc, and_, inspect, String, cast, or_
from sqlalchemy.orm import joinedload

from src.core.security import Info
from src.core.config import settings
from src.db.session import session_scope
from src.models.student_seminar import StudentSeminar
from src.models.student_manuscript import StudentManuscript
from src.models.intention_to_submit_requirement import IntentionToSubmitRequirement
from src.models.intention_to_submit import IntentionToSubmit
from src.modules.intention_to_submit_requirement.service import IntentionToSubmitRequirementService
from src.models.program import Program
from src.models.program_category import ProgramCategory
from src.modules.programs.service import ProgramService
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentSeminarInput, StudentSeminarNode, IntentionToSubmitNode, IntentionToSubmitInput, \
    IntentionToSubmitListNode, IntentionToSubmitStudentListNode, ThesisNode, ThesisListNode


class IntentionToSubmitService(CRUDBase[IntentionToSubmit, IntentionToSubmitInput, IntentionToSubmitNode]):

    @staticmethod
    def check_requirements(student_uid: str) -> List[IntentionToSubmit]:
        """
        Get Intention to Submit
        :return:
        """
        with session_scope() as session:
            stmt = select(IntentionToSubmit).where((
                                                           IntentionToSubmit.student_uid == student_uid) & (
                                                       IntentionToSubmit.deleted_at.is_(None)))
            result = session.scalars(stmt)

            # check if request is made for Intention to submit
            if result:
                print("Student Seminar ID:")

            # for seminar in result:
            #     print("Student Seminar ID:", seminar.seminar_type_id)

            return result.all()

    @staticmethod
    def get_all_intention_to_submit_paginated(info: Info, pagination, search_columns: List[str],
                                              relationships_to_join: List[str] = None,
                                              unique_search: List[dict] = None) -> [IntentionToSubmitStudentListNode]:
        """
            Get all Thesis Paginated
        :return:
        """
        with session_scope() as session:

            # if pagination.status:
            #     query = session.query(IntentionToSubmit).filter(
            #         and_(IntentionToSubmit.deleted_at.is_(None), IntentionToSubmit.status == pagination.status))
            # else:
            query = session.query(IntentionToSubmit).filter(
                IntentionToSubmit.deleted_at.is_(None))
            search_q = pagination.search if pagination.search else ''
            #
            # # filter condition if specified unique column
            unique_filter_conditions = []
            if unique_search:
                for condition in unique_search:
                    for column, value in condition.items():
                        unique_filter_conditions.append(getattr(IntentionToSubmit, column) == value)
            if unique_filter_conditions:
                query = query.filter(and_(*unique_filter_conditions))
            #
            # # Apply filters
            filter_conditions = []
            for column in inspect(IntentionToSubmit).columns:
                if column.name in search_columns:
                    filter_conditions.append(
                        cast(getattr(IntentionToSubmit, column.name), String).ilike(f"%{str(search_q)}%"))

            if filter_conditions:
                query = query.filter(or_(*filter_conditions))
            #
            total_count = query.count()
            print(total_count)
            #
            # # Apply pagination
            query = query.limit(pagination.limit).offset(pagination.offset * pagination.limit)
            # Fetch items and total count
            if relationships_to_join and len(relationships_to_join) > 0:
                for relationship_name in relationships_to_join:
                    query = query.options(joinedload(relationship_name))
            items = query.all()
            #
            if items:
                intention_to_submit_list = []
                for x in items:
                    params = {"uid": str(x.student_uid)}
                    response = requests.get(settings.UAA_URi + f'/users/student', params=params)
                    response.raise_for_status()
                    response_data = response.json()
                    if response.status_code == 200:
                        print(response_data["user"]['username'])
                        response_data = response.json()
                        info = response_data['user']
                        x.registration_number = info['username']
                        x.full_name = info['first_name'] + " " + info['middle_name'] + " " + info['last_name']

                # print(response_data)
            session.close()

            return IntentionToSubmitStudentListNode(items=items, total_count=total_count)

    @staticmethod
    def get_thesis(info: Info, pagination, search_columns: List[str],
                   relationships_to_join: List[str] = None,
                   unique_search: List[dict] = None) -> [ThesisListNode]:
        """
            Get all Thesis Paginated
        :return:
        """
        with session_scope() as session:

            # if pagination.status:
            #     query = session.query(IntentionToSubmit).filter(
            #         and_(IntentionToSubmit.deleted_at.is_(None), IntentionToSubmit.status == pagination.status))
            # else:
            # Set the Content-Type header to indicate that the request body is JSON
            headers = {
                "Content-Type": "application/json"
            }
            query = session.query(IntentionToSubmit).filter(
                IntentionToSubmit.deleted_at.is_(None))
            search_q = pagination.search if pagination.search else ''
            #
            # # filter condition if specified unique column
            unique_filter_conditions = []
            if unique_search:
                for condition in unique_search:
                    for column, value in condition.items():
                        unique_filter_conditions.append(getattr(IntentionToSubmit, column) == value)
            if unique_filter_conditions:
                query = query.filter(and_(*unique_filter_conditions))
            #
            # # Apply filters
            filter_conditions = []
            for column in inspect(IntentionToSubmit).columns:
                if column.name in search_columns:
                    filter_conditions.append(
                        cast(getattr(IntentionToSubmit, column.name), String).ilike(f"%{str(search_q)}%"))

            if filter_conditions:
                query = query.filter(or_(*filter_conditions))
            #
            total_count = query.count()
            print(total_count)
            #
            # # Apply pagination
            query = query.limit(pagination.limit).offset(pagination.offset * pagination.limit)
            # Fetch items and total count
            if relationships_to_join and len(relationships_to_join) > 0:
                for relationship_name in relationships_to_join:
                    query = query.options(joinedload(relationship_name))
            items = query.all()
            #
            if items:
                intention_to_submit_list = []
                for x in items:
                    # get seminar count
                    # student_seminar = StudentSeminarService.get_student_seminar_by_student(x.student_uid)
                    student_seminar = session.query(StudentSeminar).filter(
                        and_(StudentSeminar.deleted_at.is_(None), StudentSeminar.student_uid == x.student_uid))
                    seminar_count = student_seminar.count()
                    # get number of Manuscripts
                    student_manuscript = session.query(StudentManuscript).filter(
                        and_(StudentManuscript.deleted_at.is_(None), StudentManuscript.student_uid == x.student_uid))
                    manuscript_count = student_manuscript.count()

                    # print(x.student_uid)
                    # print(count)

                    params = {"uids": [str(x.student_uid)]}
                    # Serialize the data to JSON
                    payload = json.dumps(params)

                    response = requests.post(settings.UAA_URi + f'/students-details-by-uids', data=payload,
                                             headers=headers)
                    response.raise_for_status()
                    response_data = response.json()

                    if response.status_code == 200:
                        print(response_data)
                        # registration_number = json_data["data"][0]["registration_number"]
                        # print(response_data[0]['registration_number'])
                        # print(response_data[0]['registration_number'])
                        # print(response_data[0]['full_name'])
                        # print(response_data[0]['programme_uid'])
                        # response_data = response.json()
                        # info = response_data['data'][0]
                        x.registration_number = response_data[0]['registration_number']
                        x.full_name = response_data[0]['full_name']
                        x.program_uid = response_data[0]['programme_uid']
                        x.no_of_seminars = seminar_count
                        x.no_of_manuscripts = manuscript_count
                # print(response_data)
            session.close()

            return ThesisListNode(items=items, total_count=total_count)

    @staticmethod
    def get_all_intention_to_submit() -> Response[List[IntentionToSubmitNode]]:
        """
        Get Thesis of all student
        :param uid:
        :return StudentSeminarNode:
        """
        # Set the Content-Type header to indicate that the request body is JSON
        headers = {
            "Content-Type": "application/json"
        }

        with session_scope() as session:
            intention_to_submits = session.query(IntentionToSubmit).filter(
                IntentionToSubmit.deleted_at.is_(None)).order_by(desc(IntentionToSubmit.updated_at)).all()
            if intention_to_submits:
                student_seminar_list = []
                for x in intention_to_submits:
                    params = {"uids": [str(x.student_uid)]}
                    # response = requests.get(settings.UAA_URi + f'/users/student', params=params)
                    response = requests.get(settings.UAA_URi + f'/students-details-by-uids', params=params)
                    response.raise_for_status()
                    response_data = response.json()
                    print(response_data)
                    if response.status_code == 200:
                        print(response_data["user"]['username'])
                        response_data = response.json()
                        info = response_data['user']
                        x.registration_number = info['username']
                        x.full_name = info['first_name'] + " " + info['middle_name'] + " " + info['last_name']

                        return Response(
                            status=True,
                            code=ResponseCode.SUCCESS,
                            message="Intention to Submit Retrieved successfully",
                            data=intention_to_submits)
                    else:
                        print("response_data", response_data)
                        return Response(
                            status=False,
                            code=ResponseCode.NO_RECORD_FOUND,
                            message=response_data.get('message'),
                            data=[])
                else:
                    return Response(
                        status=True,
                        code=ResponseCode.SUCCESS,
                        message="Thesis Retrieved successfully",
                        data=[])

    @staticmethod
    def check_uniqueness(student_uid: str) -> IntentionToSubmit:
        """
        Check if there already exists Student Seminar with same course_id, program_semester_id all together
        :return ProgramCourse:
        """
        with session_scope() as session:
            stmt = select(IntentionToSubmit).where(
                (IntentionToSubmit.student_uid == student_uid) &
                (IntentionToSubmit.deleted_at.is_(None))
            )
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_intention_to_submit_by_student_uid(student_uid: str) -> List[IntentionToSubmit]:
        """
        Get Intension to Submit
        :return:
        """
        with session_scope() as session:
            stmt = select(IntentionToSubmit).where((
                                                           IntentionToSubmit.student_uid == student_uid) & (
                                                       IntentionToSubmit.deleted_at.is_(None)))

            result = session.scalars(stmt)
            # for seminar in result:
            #     print("Student Seminar ID:", seminar.seminar_type_id)

            return result.all()

    @staticmethod
    def get_intention_to_submit_by_uids(uids: List[str]) -> List[IntentionToSubmit]:
        """
        Get Thesis Submission by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(IntentionToSubmit).where(
                (IntentionToSubmit.uid.in_(uids)) & (IntentionToSubmit.deleted_at.is_(None))).order_by(
                desc(IntentionToSubmit.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_intention_to_submit_by_uid(uid: str) -> IntentionToSubmit:
        """
        Get Thesis by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(IntentionToSubmit).where(
                (IntentionToSubmit.uid == uid) & (IntentionToSubmit.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def submit_intention_to_submit(student_uid: str) -> Response[IntentionToSubmitNode]:
        """
        Register Thesis
        :param inputs:
        :return:
        """
        headers = {
            "Content-Type": "application/json"
        }
        # print(student_uid)
        # print("hhhhh")
        try:
            # Assuming you have a database session available
            with session_scope() as session:
                # Check if an intention to submit record already exists for the student
                existing_record = session.query(IntentionToSubmit).filter_by(student_uid=student_uid).first().uid
                if existing_record:
                    # print(existing_record)
                    action_name = "Submit"
                    # Get student Details
                    params = {"uids": [str(student_uid)]}
                    # Serialize the data to JSON
                    payload = json.dumps(params)
                    response = requests.post(settings.UAA_URi + f'/students-details-by-uids', data=payload,
                                             headers=headers)
                    response.raise_for_status()
                    response_data = response.json()
                    # print(response_data)
                    if response.status_code == 200:
                        # print(response_data)
                        registration_number = response_data[0]['registration_number']
                        full_name = response_data[0]['full_name']
                        program_uid = response_data[0]['programme_uid']
                        # get Seminars done
                        student_seminar = session.query(StudentSeminar).filter(
                            and_(StudentSeminar.deleted_at.is_(None), StudentSeminar.student_uid == student_uid))
                        seminar_count = student_seminar.count()
                        # get number of Manuscripts
                        # publication_status == 'accepted' OR 'published'
                        student_manuscript = session.query(StudentManuscript).filter(
                            and_(StudentManuscript.deleted_at.is_(None),
                                 StudentManuscript.student_uid == student_uid))
                        manuscript_count = student_manuscript.count()
                        no_of_seminars = seminar_count
                        no_of_manuscripts = manuscript_count
                        # print(program_uid)
                        # category = ProgramService.get_program_by_uid(program_uid)
                        # program = session.query(Program).filter_by(uid=program_uid).first()
                        # print(program.program_category_id)
                        # program = ProgramService.get_program_by_uid(program_uid)
                        # print("Program Uid ", program_uid)

                        program = session.query(Program).filter_by(uid=program_uid).first()
                        if program is None:
                            return Response(
                                status=False,
                                code=ResponseCode.FAILURE,
                                message="Invalid Student Program",
                                data=None
                            )

                        # Find Category
                        category = session.query(ProgramCategory).filter_by(id=program.program_category_id).first()
                        if category is None:
                            return Response(
                                status=False,
                                code=ResponseCode.FAILURE,
                                message="Invalid Student Program Category",
                                data=None
                            )
                            # print("Program Not Found")

                        requirements = IntentionToSubmitRequirementService. \
                            get_intention_to_submit_requirement_by_category(category.uid)
                        print(no_of_seminars)
                        print(no_of_manuscripts)
                        require_seminars = 1
                        require_manuscripts = 5
                        if no_of_seminars >= require_seminars and no_of_manuscripts >= require_manuscripts:
                            # submit
                            session.query(IntentionToSubmit).filter_by(student_uid=student_uid).update(
                                {IntentionToSubmit.status: 1})
                            session.commit()
                            return Response(
                                status=False,
                                code=ResponseCode.SUCCESS,
                                message="Submission is Successful",
                                data=None
                            )
                        else:
                            return Response(
                                status=False,
                                code=ResponseCode.FAILURE,
                                message="Submission Requirement is not Meet",
                                data=None
                            )
                else:
                    # Create a new intention to submit record
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        message="Failed to update intention to submit",
                        data=None
                    )
                    # new_record = IntentionToSubmit(student_uid=student_uid, status="Submitted")
                    # session.add(new_record)

                # Commit the changes to the database
                # session.commit()

                # Return a success response
                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Intention to submit successfully updated",
                    data=None
                )

        except Exception as e:
            print(e)
            # Return an error response if an exception occurs
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to update intention to submit",
                data=None
            )

    def register_intention_to_submit(self, inputs: List[IntentionToSubmitInput]) -> Response[IntentionToSubmitNode]:
        """
        Register Thesis
        :param inputs:
        :return:
        """
        intention_to_submit_list = []
        action_name = "Register"
        with session_scope() as session:
            # check for existing seminar types using uid
            existed_intention_to_submit = self.get_intention_to_submit_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:

                intention_to_submit_exist = self.check_uniqueness(student_uid=inputItem.student_uid)

                if inputItem.uid is None:
                    if intention_to_submit_exist:
                        return Response(
                            status=False,
                            code=ResponseCode.FAILURE,
                            data=StudentSeminarNode,
                            message="This Intention to Submit already exist"
                        )
                    intention_to_submit = IntentionToSubmit(
                        title=inputItem.title,
                        submission_date=inputItem.submission_date,
                        plagiarism_report=inputItem.plagiarism_report,
                        plagiarism_status=inputItem.plagiarism_status,
                        student_uid=inputItem.student_uid,
                        plagiarism_percentage=inputItem.plagiarism_percentage,
                        status=inputItem.status,
                    )
                    intention_to_submit_list.append(intention_to_submit)
                else:
                    action_name = "Update"
                    intention_to_submit = next(
                        filter(lambda intention_to_submit: str(intention_to_submit.uid) == str(inputItem.uid),
                               existed_intention_to_submit), None)
                    if intention_to_submit:
                        obj_data = jsonable_encoder(inputItem)
                        for key, value in obj_data.items():
                            setattr(intention_to_submit, key, value)
                        intention_to_submit_list.append(intention_to_submit)
            session.add_all(intention_to_submit_list)
            count = session.query(IntentionToSubmit).filter(IntentionToSubmit.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=intention_to_submit_list,
                            message=f"Successfully to {action_name} Intention To Submit")

    # Delete Function
    @staticmethod
    def remove_intention_to_submit(uid: str):
        """
        Remove Student seminar by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(IntentionToSubmit).filter_by(uid=uid).update({IntentionToSubmit.deleted_at: pendulum.now()})
            session.commit()


IntentionToSubmitCrud = IntentionToSubmitService(IntentionToSubmit)
