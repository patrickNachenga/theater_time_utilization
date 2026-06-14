import strawberry
from typing import List

from src.models import Region, ExternalSource
from src.modules.external_source.service import ExternalSourceService, ExternalSourceCrud
from src.modules.external_source.types import ExternalSourceInput, ExternalSourceListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.shared.excel_types import Base64ExcelOutput, Base64ExcelInput


from src.core.security import CustomPermissionExtension, Info


@strawberry.type
class ExternalSourceQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_EXTERNAL_SOURCES"])])
    def get_external_sources(self, pagination: PaginationInput) -> Response[ExternalSourceListNode]:
        try:
            result = ExternalSourceCrud.get_multi_paginated(pagination, ['name', 'code'], ExternalSourceListNode,[ExternalSource.region])
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ExternalSourceListNode(items=[], total_count=0))

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_EXTERNAL_SOURCES"])])
    def download_external_source_template(self) -> Response[Base64ExcelOutput]:
        try:
            return ExternalSourceCrud.download_template()
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to download template: {e}",
                            data=Base64ExcelOutput(file_name="", base64_data=""))


@strawberry.type
class ExternalSourceMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_EXTERNAL_SOURCES"])])
    def register_external_sources(self, inputs: List[ExternalSourceInput]) -> Response[ExternalSourceListNode]:
        try:
            return ExternalSourceService(ExternalSourceCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=ExternalSourceListNode(items=[], total_count=0))

    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_EXTERNAL_SOURCES"])])
    def import_external_sources_from_excel(self, file_input: Base64ExcelInput) -> Response[ExternalSourceListNode]:
        try:
            return ExternalSourceCrud.import_from_excel(file_input.base64_data)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to import: {e}",
                            data=ExternalSourceListNode(items=[], total_count=0))