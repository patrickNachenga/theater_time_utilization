import strawberry
from typing import List

from src.modules.death_reason.service import DeathReasonService, DeathReasonCrud
from src.modules.death_reason.types import DeathReasonInput, DeathReasonListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.shared.excel_types import Base64ExcelOutput, Base64ExcelInput


from src.core.security import CustomPermissionExtension

@strawberry.type
class DeathReasonQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_DEATH_REASONS"])])
    def get_death_reasons(self, pagination: PaginationInput) -> Response[DeathReasonListNode]:
        try:
            result = DeathReasonCrud.get_multi_paginated(pagination, ['name', 'code'], DeathReasonListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=DeathReasonListNode(items=[], total_count=0))

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_DEATH_REASONS"])])
    def download_death_reason_template(self) -> Response[Base64ExcelOutput]:
        try:
            return DeathReasonCrud.download_template()
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to download template: {e}",
                            data=Base64ExcelOutput(file_name="", base64_data=""))


@strawberry.type
class DeathReasonMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_DEATH_REASONS"])])
    def register_death_reasons(self, inputs: List[DeathReasonInput]) -> Response[DeathReasonListNode]:
        try:
            return DeathReasonService(DeathReasonCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=DeathReasonListNode(items=[], total_count=0))

    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_DEATH_REASONS"])])
    def import_death_reasons_from_excel(self, file_input: Base64ExcelInput) -> Response[DeathReasonListNode]:
        try:
            return DeathReasonCrud.import_from_excel(file_input.base64_data)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to import: {e}",
                            data=DeathReasonListNode(items=[], total_count=0))