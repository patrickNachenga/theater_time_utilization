from typing import List

import strawberry

from src.core.security import CustomPermissionExtension, Info
from src.models import TransitionMeta
from src.modules.states.service import StateCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StateInput, StateNode, PaginationInput, PaginatedState


@strawberry.type
class StateQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(['VIEW_STATES'])])
    def get_states(self, pagination: PaginationInput) -> Response[PaginatedState]:
        try:
            result = StateCrud.get_multi_paginated(pagination, ['label', 'description'], PaginatedState)
        except Exception as e:
            print(e)
            result = PaginatedState(items=[], total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve States",
            data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(['VIEW_STATES'])])
    def get_state(self, uid: str) -> Response[StateNode]:
        try:
            result = StateCrud.get(uid)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve State",
            data=result)


@strawberry.type
class StateMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(['REGISTER_STATES'])])
    def register_states(self, inputs: List[StateInput], info: Info) -> Response[PaginatedState]:
        try:
            return StateCrud.register_states(inputs, info)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to register States",
                            data=PaginatedState(items=[], total_count=0))

    @strawberry.mutation(extensions=[CustomPermissionExtension(['REMOVE_STATE'])])
    async def remove_state(self, uid: str, info: Info) -> Response[bool]:
        """
            Remove State By UID
        :param uid:
        :param info:
        :return:
        """
        try:
            StateCrud.remove_check_relations(uid, 'source_state_id', [TransitionMeta], info)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Successfully Removed State",
                data=None
            )
        except ValueError as e:
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message=str(e),
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove State",
                data=None
            )
