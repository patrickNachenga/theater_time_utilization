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
from src.modules.seminar_types.service import SeminarTypeService
from src.models.student_seminar import StudentSeminar
from src.models.intention_to_submit import IntentionToSubmit
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentSeminarInput, StudentSeminarNode, IntentionToSubmitNode, IntentionToSubmitInput, \
    IntentionToSubmitListNode, IntentionToSubmitStudentListNode


class IntentionToSubmitService(CRUDBase[IntentionToSubmit, IntentionToSubmitInput, IntentionToSubmitNode]):

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
            stmt = select(IntentionToSubmit).where((IntentionToSubmit.uid == uid) & (IntentionToSubmit.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_intention_to_submit(self, inputs: List[IntentionToSubmitInput]) -> Response[IntentionToSubmitNode]:
        """
        Register Thesis
        :param inputs:
        :return:
        """
        intention_to_submit_list = []
        action_name = "Register"
        with session_scope() as session:
            # Check if the Student Seminar already exist using uid
            # existed_student_seminar_list = self.get_student_seminar_by_names(
            #     [student_seminar.name for student_seminar in inputs if student_seminar.uid is None])
            # if existed_student_seminar_list:
            #     return Response(status=False, code=ResponseCode.DUPLICATE,
            #                     data=existed_student_seminar_list,
            #                     message="Student Seminar Already Exists")
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
