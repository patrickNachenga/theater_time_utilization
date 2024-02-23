import json
from typing import List, Optional

import strawberry

from src.core.redis import get_redis
from src.core.security import CustomPermissionExtension, Info
from src.models import Program
from src.modules.programs.service import ProgramService, ProgramCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramInput, PaginationInput, ProgramListNode, ProgramNode, ProgramCategoryNode


@strawberry.type
class ProgramQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAMS"])])
    def get_programs(self, pagination: PaginationInput, info: Info) -> Response[ProgramListNode]:
        try:

            # Enable Program List Node
            result = ProgramCrud.get_multi_paginated(pagination,
                                                     ['code', 'short_name', 'tcu_code', 'nacte_code', 'name',
                                                      'registration_code'], ProgramListNode, ["program_category"])
            # result = ProgramCrud.get_programs_with_headship(info, pagination,
            #                                                 ['code', 'short_name', 'tcu_code', 'nacte_code', 'name',
            #                                                  'registration_code'], ["program_category"])
        except Exception as e:
            print(e)
            result = ProgramListNode(items=[], total_count=0)
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Program not found",
                data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_ALL_PROGRAMS"])])
    def get_all_programs(self, pagination: PaginationInput, info: Info) -> Response[ProgramListNode]:
        try:
            result = ProgramCrud.get_multi_paginated(pagination,
                                                     ['code', 'short_name', 'tcu_code', 'nacte_code', 'name',
                                                      'registration_code'], ProgramListNode, ["program_category"])

            # result = ProgramCrud.get_multi_paginated(pagination,
            #                                          ['code', 'short_name', 'tcu_code', 'nacte_code', 'name',
            #                                           'registration_code'], ["program_category"])

        except Exception as e:
            print(e)
            result = ProgramListNode(items=[], total_count=0)
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Program not found",
                data=result)

    @staticmethod
    def program_node_to_dict(node: ProgramNode):
        return {
            "uid": node.uid,
            "code": node.code,
            "name": node.name,
            "short_name": node.short_name,
            "tcu_code": node.tcu_code,
            "nacte_code": node.nacte_code,
            "duration": node.duration,
            "program_category": {
                "uid": node.program_category.uid,
                "name": node.program_category.name,
                "short_name": node.program_category.short_name
            },
            "department_uid": node.department_uid,
            "moodle_id": node.moodle_id,
            "registration_code": node.registration_code
        }

    @strawberry.field()
    async def get_program(self, uid: str) -> Response[ProgramNode]:
        result = None
        try:
            # Try to get data from redis first; else get from the registration service
            redis = await get_redis()
            byte_data_set = await redis.smembers(f'program:{uid}')
            # decode bytes to string and parse JSON
            data_set = [json.loads(item.decode()) for item in byte_data_set]
            data = ProgramService.get_data_by_uid(data_set, uid)
            if data is None:
                result = ProgramService.get_program_by_uid(uid)
                if result:
                    await redis.sadd(f'program:{uid}', json.dumps({
                        "uid": str(result.uid),
                        "code": result.code,
                        "name": result.name,
                        "short_name": result.short_name,
                        "tcu_code": result.tcu_code,
                        "nacte_code": result.nacte_code,
                        "duration": result.duration,
                        "program_category": {
                            "uid": str(result.program_category.uid),
                            "name": result.program_category.name,
                            "short_name": result.program_category.short_name
                        },
                        "department_uid": result.department_uid,
                        "moodle_id": result.moodle_id,
                        "registration_code": result.registration_code
                    }))
            else:
                result = ProgramNode(uid=data['uid'], code=data['code'], name=data['name'],
                                     short_name=data['short_name'], tcu_code=data['tcu_code'],
                                     nacte_code=data['nacte_code'], duration=data['duration'],
                                     program_category=ProgramCategoryNode(
                                         uid=data['program_category']['uid'],
                                         short_name=data['program_category']['short_name'],
                                         name=data['program_category']['name']
                                     ), department_uid=data['department_uid'], moodle_id=data['moodle_id'],
                                     registration_code=data['registration_code'])
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Program not found",
                data=None)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAMS"])])
    def get_programs_by_program_category_uid(self, program_category_uid: str) -> Response[ProgramListNode]:
        try:
            result = ProgramService(Program).get_programs_by_category(program_category_uid)
        except Exception as e:
            print(e)
            result = ProgramListNode(items=[], total_count=0)
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Program not found",
                data=None)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAMS"])])
    def get_programs_on_program_category(self, program_uid: str) -> Response[ProgramListNode]:
        try:
            return ProgramCrud.get_programs_on_program_category(program_uid)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to get Programs",
                data=ProgramListNode(items=[], total_count=0))

    @strawberry.field()
    def get_program_name(self, program_uid: str) -> Response[str]:
        try:
            name = ProgramCrud.get_program_name(program_uid)
            if name:
                return Response(
                    status=False,
                    code=ResponseCode.SUCCESS,
                    message="Successfully retrieve program name",
                    data=name)
            else:
                return Response(
                    status=False,
                    code=ResponseCode.SUCCESS,
                    message="Failed to retrieve program name",
                    data=None)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to get Programs",
                data=None)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAMS"])])
    def get_programs_by_department_uid(self, department_uid: str) -> Response[ProgramListNode]:
        try:
            result = ProgramService(Program).get_programs_by_department(department_uid)
        except Exception as e:
            print(e)
            result = ProgramListNode(items=[], total_count=0)
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Program not found",
                data=None)


@strawberry.type
class ProgramMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_PROGRAMS"])])
    def register_program(self, inputs: List[ProgramInput]) -> Response[ProgramListNode]:
        try:
            return ProgramService(Program).register_program(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to register programs", data=[])

    # delete programs
    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_PROGRAM"])])
    async def remove_program(self, uid: str) -> Response[None]:
        """
        Remove student By UID
        :param uid:
        :return:
        """
        try:
            ProgramService.remove_program(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Program",
                data=None
            )
