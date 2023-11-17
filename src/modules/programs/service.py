from typing import List

import pendulum
import requests
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc, inspect, cast, String, or_, and_
from sqlalchemy.orm import joinedload, load_only

from src.core.config import settings
from src.core.moodle_api import MoodleApi
from src.core.security import Info
from src.db.session import session_scope
from src.helpers.utils import get_user_programs_headship, get_user_departments_headship
from src.models import AcademicYear, ProgramCategory, StudentProgramChange
from src.models.program import Program
from src.modules import CRUDBase
from src.modules.academic_year.service import AcademicYearService
from src.modules.program_category.service import ProgramCategoryService
from src.shared.models import StudentPChangeModel
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramInput, ProgramListNode, ProgramCodeInput


class ProgramService(CRUDBase[Program, ProgramInput, ProgramInput]):

    @staticmethod
    def get_programs_with_headship(info: Info, pagination, search_columns: List[str],
                                   relationships_to_join: List[str] = None,
                                   unique_search: List[dict] = None) -> [ProgramListNode]:
        """
            Get all programs by program
        :return:
        """
        with session_scope() as session:
            user_h_program_uids = get_user_programs_headship(info)
            user_h_department_uids = get_user_departments_headship(info)

            query = session.query(Program).filter(
                and_(Program.deleted_at.is_(None), or_(Program.uid.in_(user_h_program_uids),
                                                       Program.department_uid.in_(user_h_department_uids))))
            search_q = pagination.search if pagination.search else ''

            # filter condition if specified unique column
            unique_filter_conditions = []
            if unique_search:
                for condition in unique_search:
                    for column, value in condition.items():
                        unique_filter_conditions.append(getattr(Program, column) == value)
            if unique_filter_conditions:
                query = query.filter(and_(*unique_filter_conditions))

            # Apply filters
            filter_conditions = []
            for column in inspect(Program).columns:
                if column.name in search_columns:
                    filter_conditions.append(cast(getattr(Program, column.name), String).ilike(f"%{str(search_q)}%"))

            if filter_conditions:
                query = query.filter(or_(*filter_conditions))

            total_count = query.count()

            # Apply pagination
            query = query.limit(pagination.limit).offset(pagination.offset * pagination.limit)
            # Fetch items and total count
            if relationships_to_join and len(relationships_to_join) > 0:
                for relationship_name in relationships_to_join:
                    query = query.options(joinedload(relationship_name))
            items = query.all()
            session.close()

            return ProgramListNode(items=items, total_count=total_count)

    @staticmethod
    def get_programs() -> List[Program]:
        """
            Get all programs by program
        :return:
        """
        with session_scope() as session:
            result = session.query(Program).filter(Program.deleted_at.is_(None)).order_by(
                desc(Program.updated_at)).all()
            return result

    @staticmethod
    def get_program_by_uids(uids: List[str]) -> List[Program]:
        """
            Get programs by uids
        :param:uids
        :return:List[Program]
        """
        with session_scope() as session:
            stmt = select(Program).where((Program.uid.in_(uids)) & (Program.deleted_at.is_(None))).order_by(
                desc(Program.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_ids_by_uids(uids: List[str]) -> List:
        """
            Get programs_uid by uids
        :param:uids
        :return:List[str]
        """
        with session_scope() as session:
            stmt = select(Program.id, Program.uid).where(
                (Program.uid.in_(uids)) & (Program.deleted_at.is_(None))).order_by(
                desc(Program.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def api_get_program_by_departments(uids: List[str]) -> List[str]:
        """
            Get programs by department_uids
        :param:uids
        :return:List[Program]
        """
        with session_scope() as session:
            return session.query(Program.department_uid).filter(Program.department_uid.in_(uids)).order_by(
                desc(Program.updated_at)).all()

    @staticmethod
    def get_programs_by_category(category_uid: str) -> Response[ProgramListNode]:
        """
            Get programs by program category uids
        :param:category_uid
        :return:List[ProgramListNode]
        """
        with session_scope() as session:
            # Verify and get supplied program uid. and get existed year id from returned Program model
            try:
                program_category_id = ProgramCategoryService.get_program_category_by_uid(category_uid).id
            except Exception as e:
                print(e)
                return Response(status=False, code=ResponseCode.FAILURE,
                                data=ProgramListNode(items=[], total_count=0),
                                message="You have submitted incorrect program category details")

            stmt = select(Program).where(
                (Program.program_category_id == program_category_id) & (Program.deleted_at.is_(None))).order_by(
                desc(Program.updated_at))
            result = session.scalars(stmt)
            return result.all()

    def get_programs_on_program_category(self, program_uid: str) -> Response[ProgramListNode]:
        """
            Get programs by depending on the supplied program category
        :param:program_uid
        :return:List[ProgramListNode]
        """
        with session_scope() as session:
            program = self.get(program_uid)
            if program is None:
                return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                data=ProgramListNode(items=[], total_count=0),
                                message="Program Supplied Does not Exists")
            else:
                program_category_id = program.program_category.id
                result = session.query(Program).filter(Program.program_category_id == program_category_id).all()
                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Program Retrieved successfully",
                    data=ProgramListNode(items=result, total_count=len(result)))

    @staticmethod
    def get_programs_by_department(department_uid: str) -> Response[ProgramListNode]:
        """
            Get programs by department uids
        :param department_uid:
        :return List[ProgramListNode]:
        """
        with session_scope() as session:
            stmt = select(Program).where(
                (Program.department_uid == department_uid) & (Program.deleted_at.is_(None))).order_by(
                desc(Program.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_data_by_uid(data_list, uid):
        for data in data_list:
            if data['uid'] == uid:
                return data
        return None

    @staticmethod
    def get_program_by_uid(uid: str) -> Program:
        """
        Get Program by uid
        :param uid:
        :return:Program
        """
        with session_scope() as session:
            stmt = select(Program).where(
                (Program.uid == uid) & (Program.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_program_name(uid: str) -> str:
        """
        Get Program by uid
        :param uid:
        :return:Program
        """
        with session_scope() as session:
            result = session.query(Program.name).filter(Program.uid == uid).first()
            if result:
                return result.name
            else:
                return None

    @staticmethod
    def get_program_by_codes(codes: List[str]) -> List[Program]:
        """
            Get programs by codes
        :param:codes
        :return:List[Program]
        """
        with session_scope() as session:
            stmt = select(Program).where((Program.code.in_(codes)) & (Program.deleted_at.is_(None))).order_by(
                desc(Program.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_by_code(code: str) -> Program:
        """
        Get Program by code
        :param:
        :return:Program
        """
        with session_scope() as session:
            stmt = select(Program).where(
                (Program.code == code) & (Program.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_program_by_names(names: List[str]) -> List[Program]:
        """
            Get programs by names
        :param names:
        :return:List[Program]
        """
        with session_scope() as session:
            stmt = select(Program).where((Program.name.in_(names)) & (Program.deleted_at.is_(None))).order_by(
                desc(Program.updated_at))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def get_program_by_name(name: str) -> Program:
        """
        Get Program by name
        :param name:
        :return:Program
        """
        with session_scope() as session:
            stmt = select(Program).where(
                (Program.name == name) & (Program.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    # @staticmethod
    # def get_program_by_code(code: str) -> Program:
    #     """
    #     Get Program by name
    #     :param code:
    #     :return:Program
    #     """
    #     with session_scope() as session:
    #         stmt = select(Program).where(
    #             (Program.code == code) & (Program.deleted_at.is_(None)))
    #         result = session.scalars(stmt)
    #         return result.first()

    def register_program(self, inputs: List[ProgramInput]) -> Response[ProgramListNode]:
        """
        Register Program
        :param inputs:
        :return:
        """
        program_list = []
        action_type = "Register"
        with session_scope() as session:
            # Check if program already exist using code
            existed_program_code_list = self.get_program_by_codes(
                [program.code for program in inputs if program.uid is None])
            # Check if program already exist using name
            existed_program_name_list = self.get_program_by_names(
                [program.name for program in inputs if program.uid is None])
            if existed_program_code_list or existed_program_name_list:
                return Response(status=False, code=ResponseCode.DUPLICATE,
                                data=ProgramListNode(
                                    items=existed_program_code_list if existed_program_code_list is not None else existed_program_name_list,
                                    total_count=0),
                                message="Program  Already Exists")

            # check for existing Program using uid
            existed_program = self.get_program_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                # Verify and get supplied program category uid. and get existed year id from returned Program Category model
                try:
                    program_category = ProgramCategoryService.get_program_category_by_uid(
                        inputItem.program_category_uid)
                    if program_category is None:
                        raise ValueError("You have submitted incorrect programs category details")
                except Exception as e:
                    print(e)
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    data=ProgramListNode(items=[], total_count=0),
                                    message="You have submitted incorrect program category details")

                if inputItem.uid is None:
                    program = Program(
                        code=inputItem.code,
                        name=inputItem.name,
                        short_name=inputItem.short_name,
                        tcu_code=inputItem.tcu_code,
                        registration_code=inputItem.registration_code,
                        nacte_code=inputItem.nacte_code,
                        program_category=program_category,
                        department_uid=inputItem.department_uid,
                        duration=inputItem.duration,
                    )
                    session.add(program)
                    session.commit()
                    program_list.append(program)
                else:
                    action_type = "Update"
                    program = next(filter(lambda program: str(program.uid) == str(inputItem.uid),
                                          existed_program), None)
                    if program:
                        obj_data = jsonable_encoder(inputItem)
                        # Replace referenced uids field with model required ids field
                        obj_data['program_category_id'] = program_category.id
                        for key, value in obj_data.items():
                            setattr(program, key, value)

                        session.add(program)
                        session.commit()
                        program_list.append(program)
            count = session.query(Program).filter(Program.deleted_at.is_(None)).count()
            session.commit()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=ProgramListNode(items=program_list, total_count=count),
                            message=f"Successfully to {action_type} Program")

    @staticmethod
    def remove_program(uid: str):
        """
        Remove Program by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(Program).filter_by(uid=uid).update({Program.deleted_at: pendulum.now()})
            session.commit()

    @staticmethod
    async def api_get_program_by(code: str | None = None, uid: str | None = None) -> Response:
        """
            Get programs by codes
        :param:
        """
        try:
            with session_scope() as session:
                if code:
                    # program = ProgramService.get_program_by_code(code)
                    program = session.query(Program).options(
                        load_only("uid", "code", "registration_code", "name", "short_name", "duration",
                                  "department_uid", "program_category_id")).join(ProgramCategory).filter(
                        Program.code == code).first()
                elif uid:
                    # program = ProgramService.get_program_by_uid(uid)
                    program = session.query(Program).options(
                        load_only("uid", "code", "registration_code", "name", "short_name", "duration",
                                  "department_uid", "program_category_id")).join(ProgramCategory).filter(
                        Program.uid == uid).first()
                else:
                    return Response(status=False, code=ResponseCode.FAILURE,
                                    message=f"Invalid inputs supplied!", data={})

                # academic_year:AcademicYear
                # academic_year = AcademicYearService.get_active_academic_year()
                academic_year = session.query(AcademicYear.id, AcademicYear.uid, AcademicYear.name).filter(
                    AcademicYear.status == 1).first()
                # print("program", program)

                return Response(status=True, code=ResponseCode.SUCCESS, data={
                    "uid": program.uid,
                    "code": program.code,
                    "registration_code": program.registration_code,
                    "name": program.name,
                    "short_name": program.short_name,
                    "duration": program.duration,
                    "department_uid": program.department_uid,
                    "program_category_name": program.program_category.name,
                    "program_category_short_name": program.program_category.short_name,
                    "active_academic_year": academic_year.name,
                    "active_academic_year_uid": academic_year.uid

                }, message="Program retrieved Successfully")
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE,
                            message=f"fail to find program", data={})

    @staticmethod
    async def api_get_programs() -> Response:
        """
            Get all programs
        :param:
        """
        try:
            with session_scope() as session:
                # program = ProgramService(Program).get_programs()
                program = session.query(Program).options(
                    load_only("uid", "code", "registration_code", "name", "short_name", "duration",
                              "department_uid", "program_category_id")).join(ProgramCategory).all()
                if program:
                    return Response(status=True, code=ResponseCode.SUCCESS, data=[{
                        "uid": programItems.uid,
                        "code": programItems.code,
                        "registration_code": programItems.registration_code,
                        "name": programItems.name,
                        "short_name": programItems.short_name,
                        "department_uid": programItems.department_uid,
                        "duration": programItems.duration,
                        "program_category_name": programItems.program_category.name,
                        "program_category_short_name": programItems.program_category.short_name,
                    } for programItems in program],
                                    message="Program retrieved Successfully")
                else:
                    return Response(status=False, code=ResponseCode.NO_RECORD_FOUND, data=[],
                                    message="No program found")
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE,
                            message=f"Unable to find programs", data=None)

    @staticmethod
    async def api_get_program_name_duration(uid) -> Response:

        try:
            with session_scope() as session:
                # program = ProgramService(Program).get_programs()
                program = session.query(Program.duration, Program.name).filter(Program.uid == uid).first()
                if program:
                    return Response(status=True, code=ResponseCode.SUCCESS, data={
                        "name": program.name,
                        "duration": program.duration
                    },
                                    message="Program retrieved Successfully")
                else:
                    return Response(status=False, code=ResponseCode.NO_RECORD_FOUND, data=[],
                                    message="No program found")
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE,
                            message=f"Unable to find programs", data=None)

    @staticmethod
    async def api_get_uqf_pchanges_list(student_input: StudentPChangeModel) -> Response:

        try:
            with (session_scope() as session):

                # Query the database to find the record
                record = session.query(StudentProgramChange).filter(
                    student_input.registration_number == StudentProgramChange.current_registration_number).first()

                # Update the remarks field
                if record:
                    record.remarks = student_input.remarks
                    session.commit()
                    session.refresh(record)
                    return Response(status=True, code=ResponseCode.SUCCESS, data=[],
                                    message="Program change updated Successfully")
                else:
                    return {'status': False, 'code': ResponseCode.FAILURE,
                            'data': '', 'message': "Failed to update student"}

        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE,
                            message=f"Unable to find students for program change", data=None)

    @staticmethod
    async def api_get_program_change_student_list() -> Response:

        try:
            with (session_scope() as session):
                # program = ProgramService(Program).get_programs()
                program_change_data = session.query(StudentProgramChange.student_uid,
                                                    StudentProgramChange.new_program_id,
                                                    Program.uid,
                                                    Program.name,
                                                    Program.code,
                                                    Program.registration_code,
                                                    StudentProgramChange.current_program_id,
                                                    StudentProgramChange.current_registration_number,
                                                    StudentProgramChange.reason,
                                                    StudentProgramChange.academic_year,
                                                    StudentProgramChange.approve_status
                                                    ).join(Program,
                                                           StudentProgramChange.new_program_id == Program.id).all()
                if program_change_data:
                    print('Data zimekujaa')
                    return Response(status=True, code=ResponseCode.SUCCESS, data=program_change_data,
                                    message="Program change retrieved Successfully")
                else:
                    print('Data holaaaa')
                    return Response(status=False, code=ResponseCode.NO_RECORD_FOUND, data=[],
                                    message="No students for program change found")
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE,
                            message=f"Unable to find students for program change", data=None)


ProgramCrud = ProgramService(Program)
