import json
import uuid
from typing import List

import pendulum
import requests
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc, and_, inspect, String, cast, or_
from sqlalchemy.orm import joinedload

from src.core.config import settings
from src.db.session import session_scope
from src.modules.seminar_types.service import SeminarTypeService
from src.models.student_seminar import StudentSeminar
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentSeminarInput, StudentSeminarNode, StudentSeminarListNode, AllStudentSeminarNode


class StudentSeminarService(CRUDBase[StudentSeminar, StudentSeminarInput, StudentSeminarInput]):
    @staticmethod
    def get_student_seminars_page(pagination, unique_search: [], search_columns: [],
                             relationships_to_join: []) -> Response[StudentSeminarListNode]:
        with session_scope() as session:
            query = session.query(StudentSeminar).filter(StudentSeminar.deleted_at.is_(None))
            search_q = pagination.search if pagination.search else ''

            # filter condition if specified unique column
            unique_filter_conditions = []
            if unique_search:
                for condition in unique_search:
                    for column, value in condition.items():
                        unique_filter_conditions.append(getattr(StudentSeminar, column) == value)
            if unique_filter_conditions:
                query = query.filter(and_(*unique_filter_conditions))

            # Apply filters
            filter_conditions = []
            for column in inspect(StudentSeminar).columns:
                if column.name in search_columns:
                    filter_conditions.append(
                        cast(getattr(StudentSeminar, column.name), String).ilike(f"%{str(search_q)}%"))

            if filter_conditions:
                query = query.filter(or_(*filter_conditions))

            total_count = query.count()

            # Apply pagination
            # Query and retrieve the list of student UIDs
            student_uids = session.query(StudentSeminar.student_uid).all()

            # Extract the UIDs from the query result
            uids_list = [uid for uid, in student_uids]

            print(student_uids)
            # student_uids = query.all()

            query = query.limit(pagination.limit).offset(pagination.offset * pagination.limit)
            # Fetch items and total count
            if relationships_to_join and len(relationships_to_join) > 0:
                for relationship_name in relationships_to_join:
                    query = query.options(joinedload(relationship_name))

            # get students from UAA
            # Serialize the data to JSON
            data_json = json.dumps(uids_list)

            # Set the Content-Type header to indicate that the request body is JSON
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.post(settings.UAA_URi + '/students-details-by-uids', data=data_json, headers=headers)
            print(response.status_code)
            if response.status_code == 200:
                response_data = response.json()
                print("response_data")
                if response_data["status"]:
                    pass

            else:
                print(response.json())
                return Response(status=False, message="Failed", code=ResponseCode.BAD_REQUEST,
                                data=StudentSeminarListNode(items=[], total_count=0))

            session.close()

            return Response(status=False, message="Failed", code=ResponseCode.BAD_REQUEST,
                            data=StudentSeminarListNode(items=query.all(), total_count=query.count()))

    @staticmethod
    def get_all_student_seminars() -> Response[List[AllStudentSeminarNode]]:
        """
        Get Student Seminars of all student
        :param uid:
        :return StudentSeminarNode:
        """
        # Set the Content-Type header to indicate that the request body is JSON
        headers = {
            "Content-Type": "application/json"
        }

        with session_scope() as session:
            student_seminars = session.query(StudentSeminar).filter(
                StudentSeminar.deleted_at.is_(None)).order_by(desc(StudentSeminar.updated_at)).all()
            if student_seminars:
                for student_seminar_array in student_seminars:
                    student_uid = str(student_seminar_array.student_uid)

                    params = {"uid": student_uid}
                    response = requests.get(settings.UAA_URi + f'/users/student', params=params)
                    response.raise_for_status()
                    print(response.json())

                students_uids = [str(student_seminar.student_uid) for student_seminar in student_seminars]
                params = {"uids": students_uids}
                # print(params)

                response = requests.post(settings.UAA_URi + f'/students-details-by-uids', data=json.dumps(params),
                                         headers=headers)
                print(response.json())
                # print(response.status_code)
                # student_seminar_list = []
                if response.status_code == 200:
                    response_data = response.json()
                    # print(response_data.get('status'))
                    if response_data and response_data.get('status'):
                        response_data = response.json()
                        for x in student_seminars:
                            filtered_students = [student for student in response_data.get("data") if
                                                 student['registration_number'] == 'CIT/D/2023/0001']
                            if filtered_students:
                                st = filtered_students[0]
                                x.full_name = st['full_name']
                                x.registration_number = st['registration_number']
                                # student_seminar_list.append(x)
                                # print(x)

                        return Response(
                            status=True,
                            code=ResponseCode.SUCCESS,
                            message="Student Seminar Retrieved successfully",
                            data=student_seminars)

                        # filtered_students = [student for student in students if student["age"] > age_threshold]

                        for structure in response_data["data"]:
                            student_seminar_structure = AllStudentSeminarNode(
                                registration_number=structure["registration_number"],
                                student_uid=structure["student_uid"]
                            )
                            print(structure["registration_number"])
                            # student_seminar_list.append(student_seminar_structure)
                            return Response(
                                status=True,
                                code=ResponseCode.SUCCESS,
                                message="Student Seminars Retrieved successfully",
                                data=student_seminar_list)
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
                        message="Student Seminar Retrieved successfully",
                        data=[])

    @staticmethod
    def get_student_seminar_by_names(uid: List[str]) -> List[StudentSeminar]:
        """
        Get seminar Type by names
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentSeminar).where(
                (StudentSeminar.uid.in_(uid)) & (StudentSeminar.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def check_uniqueness(student_uid: str, seminar_type_id: int) -> StudentSeminar:
        """
        Check if there already exists Student Seminar with same course_id, program_semester_id all together
        :return ProgramCourse:
        """
        with session_scope() as session:
            stmt = select(StudentSeminar).where(
                (StudentSeminar.seminar_type_id == seminar_type_id) &
                (StudentSeminar.student_uid == student_uid) &
                (StudentSeminar.deleted_at.is_(None))
            )
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_student_seminar_by_student_uid(inputs) -> List[StudentSeminar]:
        """
        Get Student seminar  by Student Uid
        :return:
        """
        with session_scope() as session:
            if inputs.seminar_type_uid:
                try:
                    seminar_type = SeminarTypeService.get_seminar_type_by_uid(inputs.seminar_type_uid)
                except Exception as e:
                    print(e)
                    return []
                if seminar_type is None:
                    return []
                stmt = select(StudentSeminar).where((StudentSeminar.student_uid == inputs.student_uid) & (
                    StudentSeminar.deleted_at.is_(None)) &
                                                    (StudentSeminar.seminar_type_id == seminar_type.id)
                                                    )
            else:
                stmt = select(StudentSeminar).where((
                                                            StudentSeminar.student_uid == inputs.student_uid) & (
                                                        StudentSeminar.deleted_at.is_(None)))

            result = session.scalars(stmt)
            # for seminar in result:
            #     print("Student Seminar ID:", seminar.seminar_type_id)

            return result.all()

    @staticmethod
    def get_student_seminar_by_uids(uids: List[str]) -> List[StudentSeminar]:
        """
        Get Student Seminar by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentSeminar).where(
                (StudentSeminar.uid.in_(uids)) & (StudentSeminar.deleted_at.is_(None))).order_by(
                desc(StudentSeminar.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_student_seminar_by_uid(uid: str) -> StudentSeminar:
        """
        Get seminar_type by uid
        :param uid:
        :return:
        """
        with session_scope() as session:
            stmt = select(StudentSeminar).where((StudentSeminar.uid == uid) & (StudentSeminar.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    def register_student_seminar(self, inputs: List[StudentSeminarInput]) -> Response[StudentSeminarNode]:
        """
        Register Seminar Types
        :param inputs:
        :return:
        """
        student_seminar_list = []
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
            existed_student_seminar = self.get_student_seminar_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:

                # Verify and get supplied Seminar Type uid. and get existed Seminar Type id from returned Seminar Type model
                seminar_type = SeminarTypeService.get_seminar_type_by_uid(inputItem.seminar_types_uid)
                if seminar_type is None:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=StudentSeminarNode,
                        message="You have submitted incorrect Seminar Type details"
                    )
                print(inputItem.student_uid)
                print(seminar_type.id)
                student_seminar_exist = self.check_uniqueness(student_uid=inputItem.student_uid,
                                                              seminar_type_id=seminar_type.id)

                if inputItem.uid is None:
                    if student_seminar_exist:
                        return Response(
                            status=False,
                            code=ResponseCode.FAILURE,
                            data=StudentSeminarNode,
                            message="This Seminar already exist for the Student"
                        )
                    student_seminar = StudentSeminar(
                        title=inputItem.title,
                        seminar_date=inputItem.seminar_date,
                        is_pass=inputItem.is_pass,
                        seminar_marks=inputItem.seminar_marks,
                        student_uid=inputItem.student_uid,
                        seminar_types=seminar_type,
                        description=inputItem.description,
                        status=inputItem.status,
                    )
                    student_seminar_list.append(student_seminar)
                else:
                    action_name = "Update"
                    student_seminar = next(
                        filter(lambda student_seminar: str(student_seminar.uid) == str(inputItem.uid),
                               existed_student_seminar), None)
                    if student_seminar:
                        obj_data = jsonable_encoder(inputItem)
                        for key, value in obj_data.items():
                            setattr(student_seminar, key, value)
                        student_seminar_list.append(student_seminar)
            session.add_all(student_seminar_list)
            count = session.query(StudentSeminar).filter(StudentSeminar.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=student_seminar_list,
                            message=f"Successfully to {action_name} Student Seminar")

    # Delete Function
    @staticmethod
    def remove_student_seminar(uid: str):
        """
        Remove Student seminar by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(StudentSeminar).filter_by(uid=uid).update({StudentSeminar.deleted_at: pendulum.now()})
            session.commit()


StudentSeminarCrud = StudentSeminarService(StudentSeminar)
