import strawberry
from typing import List

from src.modules.procedure.service import ProcedureService, ProcedureCrud
from src.modules.procedure.types import ProcedureInput, ProcedureListNode
from src.shared.excel_types import Base64ExcelOutput, Base64ExcelInput
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


from src.core.security import CustomPermissionExtension

@strawberry.type
class ProcedureQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROCEDURES"])])
    def get_procedures(self, pagination: PaginationInput) -> Response[ProcedureListNode]:
        try:
            result = ProcedureCrud.get_multi_paginated(pagination, ['name', 'code'], ProcedureListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ProcedureListNode(items=[], total_count=0))

    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_PROCEDURES"])])
    def download_procedure_template(self) -> Response[Base64ExcelOutput]:
        try:
            return ProcedureCrud.download_template()
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to download template: {e}",
                            data=Base64ExcelOutput(file_name="", base64_data=""))


@strawberry.type
class ProcedureMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_PROCEDURES"])])
    def register_procedures(self, inputs: List[ProcedureInput]) -> Response[ProcedureListNode]:
        try:
            return ProcedureService(ProcedureCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ProcedureListNode(items=[], total_count=0))



    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_PROCEDURES"])])
    def import_procedure_from_excel(self, file_input: Base64ExcelInput) -> Response[ProcedureListNode]:
        try:
            return ProcedureCrud.import_from_excel(file_input.base64_data)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to import: {e}",
                            data=ProcedureListNode(items=[], total_count=0))
