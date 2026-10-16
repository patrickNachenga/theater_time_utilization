import strawberry
from typing import List, Optional

from src.models import TheatreRoom
from src.modules.theatre_room.service import TheatreRoomService, TheatreRoomCrud
from src.modules.theatre_room.types import TheatreRoomInput, TheatreRoomListNode, TheatreRoomStatus
from src.modules.theatre_unit.service import TheatreUnitCrud
from src.types import PaginationInput
from src.shared.response import Response
from src.shared.response_code import ResponseCode

from src.core.security import CustomPermissionExtension, Info


@strawberry.type
class TheatreRoomQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_ROOMS"])])
    def get_theatre_rooms(self, pagination: PaginationInput,
                         theatre_unit_uid: Optional[str] = None) -> Response[TheatreRoomListNode]:
        try:
            unique_search = None
            if theatre_unit_uid:
                theatre_unit = TheatreUnitCrud.get(theatre_unit_uid)
                if not theatre_unit:
                    return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved",
                                    data=TheatreRoomListNode(items=[], total_count=0))
                unique_search = [{"theatre_unit_id": theatre_unit.id}]

            result = TheatreRoomCrud.get_multi_paginated(
                pagination, ["name", "code", "category"], TheatreRoomListNode,
                relationships_to_join=[TheatreRoom.theatre_unit],
                unique_search=unique_search,
            )
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=result)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed",
                            data=TheatreRoomListNode(items=[], total_count=0))


@strawberry.type
class TheatreRoomMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_ROOMS"])])
    def register_theatre_rooms(self, inputs: List[TheatreRoomInput], info: Info) -> Response[TheatreRoomListNode]:
        try:
            return TheatreRoomService(TheatreRoomCrud.model).register(inputs, info=info)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed",
                            data=TheatreRoomListNode(items=[], total_count=0))

    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_ROOMS"])])
    def set_theatre_room_status(self, uid: str, status: TheatreRoomStatus, info: Info) -> Response[TheatreRoomListNode]:
        try:
            return TheatreRoomService(TheatreRoomCrud.model).set_status(uid, status, info=info)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to update status",
                            data=TheatreRoomListNode(items=[], total_count=0))
