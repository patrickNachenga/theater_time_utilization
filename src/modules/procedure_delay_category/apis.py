import strawberry
from typing import List

from src.modules.procedure_delay_category.service import ProcedureDelayCategoryService, ProcedureDelayCategoryCrud
from src.modules.procedure_delay_category.types import ProcedureDelayCategoryInput, ProcedureDelayCategoryListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.shared.excel_types import Base64ExcelOutput, Base64ExcelInput


from src.core.security import CustomPermissionExtension

@strawberry.type
class ProcedureDelayCategoryQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROCEDURE_DELAY_CATEGORIES"])])
    def get_procedure_delay_categories(self, pagination: PaginationInput) -> Response[ProcedureDelayCategoryListNode]:
        try:
            result = ProcedureDelayCategoryCrud.get_multi_paginated(pagination, ['name', 'code', 'description'], ProcedureDelayCategoryListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ProcedureDelayCategoryListNode(items=[], total_count=0))

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROCEDURE_DELAY_CATEGORIES"])])
    def download_procedure_delay_category_template(self) -> Response[Base64ExcelOutput]:
        try:
            return ProcedureDelayCategoryCrud.download_template()
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to download template: {e}",
                            data=Base64ExcelOutput(file_name="", base64_data=""))


@strawberry.type
class ProcedureDelayCategoryMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_PROCEDURE_DELAY_CATEGORIES"])])
    def register_procedure_delay_categories(self, inputs: List[ProcedureDelayCategoryInput]) -> Response[ProcedureDelayCategoryListNode]:
        try:
            return ProcedureDelayCategoryService(ProcedureDelayCategoryCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ProcedureDelayCategoryListNode(items=[], total_count=0))

    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_PROCEDURE_DELAY_CATEGORIES"])])
    def import_procedure_delay_categories_from_excel(self, file_input: Base64ExcelInput) -> Response[ProcedureDelayCategoryListNode]:
        try:
            return ProcedureDelayCategoryCrud.import_from_excel(file_input.base64_data)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to import: {e}",
                            data=ProcedureDelayCategoryListNode(items=[], total_count=0))