from typing import List

import strawberry

from src.core.security import CustomPermissionExtension, Info
from src.models import TransitionMeta
from src.modules.workflows.service import WorkflowCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import WorkflowInput, WorkflowNode, PaginationInput, PaginatedWorkflow


@strawberry.type
class WorkflowQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(['VIEW_WORKFLOWS'])])
    def get_workflows(self, pagination: PaginationInput) -> Response[PaginatedWorkflow]:
        try:
            result = WorkflowCrud.get_multi_paginated(pagination, ['name', 'description'], PaginatedWorkflow)
        except Exception as e:
            print(e)
            result = PaginatedWorkflow(items=[], total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Workflows",
            data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(['VIEW_WORKFLOWS'])])
    def get_workflow(self, uid: str) -> Response[WorkflowNode]:
        try:
            result = WorkflowCrud.get(uid)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Workflow",
            data=result)


@strawberry.type
class WorkflowMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(['REGISTER_WORKFLOWS'])])
    def register_workflows(self, inputs: List[WorkflowInput], info: Info) -> Response[PaginatedWorkflow]:
        try:
            return WorkflowCrud.register_workflows(inputs, info)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to register Workflows",
                            data=PaginatedWorkflow(items=[], total_count=0))

    @strawberry.mutation(extensions=[CustomPermissionExtension(['REMOVE_WORKFLOW'])])
    async def remove_workflow(self, uid: str, info: Info) -> Response[bool]:
        """
            Remove Workflow By UID
        :param uid:
        :param info:
        :return:
        """
        try:
            WorkflowCrud.remove_check_relations(uid, 'workflow_id', [TransitionMeta], info)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Successfully Removed Workflow",
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
                message="Failed to Remove Workflow",
                data=None
            )
