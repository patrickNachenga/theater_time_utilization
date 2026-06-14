import strawberry
from typing import List

from src.modules.theatre_unit.service import TheatreUnitService, TheatreUnitCrud
from src.modules.theatre_unit.types import TheatreUnitInput, TheatreUnitListNode
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.shared.excel_types import Base64ExcelOutput, Base64ExcelInput


from src.core.security import CustomPermissionExtension

@strawberry.type
class TheatreUnitQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_UNITS"])])
    def get_theatre_units(self, pagination: PaginationInput) -> Response[TheatreUnitListNode]:
        try:
            result = TheatreUnitCrud.get_multi_paginated(pagination, ['name', 'code', 'location'], TheatreUnitListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreUnitListNode(items=[], total_count=0))

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_UNITS"])])
    def download_theatre_unit_template(self) -> Response[Base64ExcelOutput]:
        try:
            return TheatreUnitCrud.download_template()
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to download template: {e}",
                            data=Base64ExcelOutput(file_name="", base64_data=""))


@strawberry.type
class TheatreUnitMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_UNITS"])])
    def register_theatre_units(self, inputs: List[TheatreUnitInput]) -> Response[TheatreUnitListNode]:
        try:
            return TheatreUnitService(TheatreUnitCrud.model).register(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreUnitListNode(items=[], total_count=0))

    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_UNITS"])])
    def import_theatre_units_from_excel(self, file_input: Base64ExcelInput) -> Response[TheatreUnitListNode]:
        try:
            return TheatreUnitCrud.import_from_excel(file_input.base64_data)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to import: {e}",
                            data=TheatreUnitListNode(items=[], total_count=0))