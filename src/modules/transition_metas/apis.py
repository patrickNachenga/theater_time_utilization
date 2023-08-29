from typing import List

import strawberry

from src.core.security import CustomPermissionExtension, Info
from src.modules.transition_metas.service import TransitionMetaCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import TransitionMetaNode, PaginationInput, PaginatedTransitionMeta, TransitionMetaInput


@strawberry.type
class TransitionMetaQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(['VIEW_TRANSITION_METAS'])])
    def get_transition_metas(self, pagination: PaginationInput) -> Response[PaginatedTransitionMeta]:
        try:
            result = TransitionMetaCrud.get_multi_paginated(pagination, [], PaginatedTransitionMeta)
        except Exception as e:
            print(e)
            result = PaginatedTransitionMeta(items=[], total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve TransitionMetas",
            data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(['VIEW_TRANSITION_METAS'])])
    def get_transition_meta(self, uid: str) -> Response[TransitionMetaNode]:
        try:
            result = TransitionMetaCrud.get(uid)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve TransitionMeta",
            data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(['VIEW_TRANSITION_METAS'])])
    def get_transition_meta_by_workflow(self, workflow_uid: str) -> Response[List[TransitionMetaNode]]:
        try:
            result = TransitionMetaCrud.get_transition_metas_by_workflow(workflow_uid)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve TransitionMeta",
            data=result)


@strawberry.type
class TransitionMetaMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(['REGISTER_TRANSITION_METAS'])])
    def register_transition_metas(self, inputs: List[TransitionMetaInput], info: Info) -> (
            Response)[PaginatedTransitionMeta]:
        try:
            return TransitionMetaCrud.register_transition_metas(inputs, info)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to register TransitionMetas",
                            data=PaginatedTransitionMeta(items=[], total_count=0))

    @strawberry.mutation(extensions=[CustomPermissionExtension(['REMOVE_TRANSITION_META'])])
    async def remove_transition_meta(self, uid: str, info: Info) -> Response[bool]:
        """
            Remove Transition Meta By UID
        :param uid:
        :param info:
        :return:
        """
        try:
            TransitionMetaCrud.remove_check_relations(uid, 'transition_meta_id', [], info)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Successfully Removed TransitionMeta",
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
                message="Failed to Remove Transition Meta",
                data=None
            )
