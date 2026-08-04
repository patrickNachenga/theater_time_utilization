import strawberry
from typing import List

from src.modules.theatre_member.service import TheatreMemberService, TheatreMemberCrud
from src.modules.theatre_member.types import TheatreMemberInput, TheatreMemberListNode, ImportResultNode
from src.shared.excel_types import Base64ExcelOutput, Base64ExcelInput
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode


from src.core.security import CustomPermissionExtension, Info


@strawberry.type
class TheatreMemberQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_MEMBERS"])])
    def get_theatre_members(self, pagination: PaginationInput) -> Response[TheatreMemberListNode]:
        try:
            result = TheatreMemberCrud.get_multi_paginated(pagination, ['first_name', 'last_name', 'pf_number'], TheatreMemberListNode)
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreMemberListNode(items=[], total_count=0))


    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_MEMBERS"])])
    def download_theatre_member_template(self) -> Response[Base64ExcelOutput]:
        try:
            return TheatreMemberCrud.download_template()
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to download template: {e}",
                            data=Base64ExcelOutput(file_name="", base64_data=""))


@strawberry.type
class TheatreMemberMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_MEMBERS"])])
    def register_theatre_members(self, inputs: List[TheatreMemberInput],  info: Info) -> Response[TheatreMemberListNode]:
        try:
            return TheatreMemberService(TheatreMemberCrud.model).register(inputs, info=info)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=TheatreMemberListNode(items=[], total_count=0))

    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_MEMBERS"])])
    async def import_theatre_members_from_excel(self, file_input: Base64ExcelInput, info: Info) -> Response[ImportResultNode]:
        try:
            data = TheatreMemberCrud.import_from_excel(file_input.base64_data, info)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message=f"Import Process completed:",
                data=data
            )
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message=f"Failed to import: {e}",
                            data=ImportResultNode(successful_count=0, failed_count=0, failed_records_file=None))