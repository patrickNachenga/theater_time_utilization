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
from src.models.student_manuscript import StudentManuscript
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentManuscriptInput, StudentManuscriptNode, StudentManuscriptAllListNode


class StudentManuscriptService(CRUDBase[StudentManuscript, StudentManuscriptInput, StudentManuscriptNode]):

    @staticmethod
    def get_all_manuscript_paginated(info: Info, pagination, search_columns: List[str],
                                          relationships_to_join: List[str] = None,
                                          unique_search: List[dict] = None) -> [StudentManuscriptAllListNode]:
        """
            Get all Manuscript Paginated
        :return:
        """
        with session_scope() as session:

            # if pagination.status:
            #     query = session.query(IntentionToSubmit).filter(
            #         and_(IntentionToSubmit.deleted_at.is_(None), IntentionToSubmit.status == pagination.status))
            # else:
            query = session.query(StudentManuscript).filter(
                    StudentManuscript.deleted_at.is_(None))
            search_q = pagination.search if pagination.search else ''
            #
            # # filter condition if specified unique column
            unique_filter_conditions = []
            if unique_search:
                for condition in unique_search:
                    for column, value in condition.items():
                        unique_filter_conditions.append(getattr(StudentManuscript, column) == value)
            if unique_filter_conditions:
                query = query.filter(and_(*unique_filter_conditions))
            #
            # # Apply filters
            filter_conditions = []
            for column in inspect(StudentManuscript).columns:
                if column.name in search_columns:
                    filter_conditions.append(
                        cast(getattr(StudentManuscript, column.name), String).ilike(f"%{str(search_q)}%"))

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

            session.close()

            return StudentManuscriptAllListNode(items=items, total_count=total_count)

    @staticmethod
    def get_student_manuscript_by_student_uid(student_uid) -> List[StudentManuscript]:
        """
        Get Student Manuscript  by Student Uid
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentManuscript).where((
                               StudentManuscript.student_uid == student_uid) & (
                           StudentManuscript.deleted_at.is_(None)))
            result = session.scalars(stmt)

            return result.all()

    @staticmethod
    def check_uniqueness(student_uid: str, title: str) -> StudentManuscript:
        """
        Check if there already exists Student Manuscript with same title exist,
        :return StudentManuscript:
        """
        with session_scope() as session:
            stmt = select(StudentManuscript).where(
                (StudentManuscript.title == title) &
                (StudentManuscript.student_uid == student_uid) &
                (StudentManuscript.deleted_at.is_(None))
            )
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_student_manuscript() -> Response[StudentManuscript]:
        """
        Get seminar manuscript
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentManuscript).where((StudentManuscript.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_student_manuscript_by_uid(uid: str) -> Response[StudentManuscript]:
        """
        Get seminar_type by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentManuscript).where(
                (StudentManuscript.uid == uid) &
                (StudentManuscript.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_student_manuscript_by_uids(uids: List[str]) -> List[StudentManuscript]:
        """
        Get Student Manuscript by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentManuscript).where(
                (StudentManuscript.uid.in_(uids)) & (StudentManuscript.deleted_at.is_(None))).order_by(
                desc(StudentManuscript.updated_at))
            result = session.scalars(stmt)
            return result.all()

    def register_student_manuscript(self, inputs: List[StudentManuscriptInput]) -> Response[StudentManuscriptNode]:
        """
        Register Student Manuscript Types
        :param inputs:
        :return:
        """
        student_manuscript_list = []
        action_name = "Register"
        with session_scope() as session:
            existed_student_manuscript = self.get_student_manuscript_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:

                print(inputItem.student_uid)
                print(inputItem.title)
                student_seminar_exist = self.check_uniqueness(student_uid=inputItem.student_uid,
                                                              title=inputItem.title)

                if inputItem.uid is None:
                    if student_seminar_exist:
                        return Response(
                            status=False,
                            code=ResponseCode.DUPLICATE,
                            data=StudentManuscriptNode,
                            message="This Student Manuscript Title already exist for the Student"
                        )
                    student_manuscript = StudentManuscript(
                        title=inputItem.title,
                        publication_date=inputItem.publication_date,
                        publication_status=inputItem.publication_status,
                        student_uid=inputItem.student_uid,
                        description=inputItem.description,
                        status=inputItem.status,
                    )
                    student_manuscript_list.append(student_manuscript)
                else:
                    action_name = "Update"
                    student_manuscript = next(
                        filter(lambda student_manuscript: str(student_manuscript.uid) == str(inputItem.uid),
                               existed_student_manuscript), None)
                    if student_manuscript:
                        obj_data = jsonable_encoder(inputItem)
                        for key, value in obj_data.items():
                            setattr(student_manuscript, key, value)
                        student_manuscript_list.append(student_manuscript)
            session.add_all(student_manuscript_list)
            count = session.query(StudentManuscript).filter(StudentManuscript.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=student_manuscript,
                            message=f"Successfully to {action_name} Student Manuscript")

    # Delete Function
    @staticmethod
    def remove_student_manuscript(uid: str):
        """
        Remove Student Manuscript by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(StudentManuscript).filter_by(uid=uid).update({StudentManuscript.deleted_at: pendulum.now()})
            session.commit()


StudentManuscriptCrud = StudentManuscriptService(StudentManuscript)
