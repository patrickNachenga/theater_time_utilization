from typing import List, Optional

from src.core.security import Info
from src.database.session import session_scope
from src.modules import CRUDBase
from src.models import TheatreRoom
from src.modules.theatre_room.types import TheatreRoomInput, TheatreRoomListNode, TheatreRoomStatus
from src.modules.theatre_unit.service import TheatreUnitCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode


class TheatreRoomService(CRUDBase[TheatreRoom, TheatreRoomInput, TheatreRoomInput]):
    def register(self, inputs: List[TheatreRoomInput], info: Optional[Info] = None) -> Response[TheatreRoomListNode]:
        """
        Upserts rooms by uid, scoped to their theatre unit. Unlike the generic
        create_or_update helper (which treats its unique field as global),
        room names only need to be unique *within* a unit, so that check is
        left to the DB's (theatre_unit_id, name) unique constraint.
        """
        try:
            username = self._get_user_name(info)

            with session_scope() as session:
                for input_obj in inputs:
                    theatre_unit = TheatreUnitCrud.get(input_obj.theatre_unit_uid)
                    if not theatre_unit:
                        return Response(status=False, code=ResponseCode.FAILURE,
                                        message="Theatre Unit not found.",
                                        data=TheatreRoomListNode(items=[], total_count=0))

                    if input_obj.uid:
                        room = (
                            session.query(TheatreRoom)
                            .filter(TheatreRoom.uid == input_obj.uid, TheatreRoom.deleted_at.is_(None))
                            .first()
                        )
                        if not room:
                            return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                            message="Theatre Room not found.",
                                            data=TheatreRoomListNode(items=[], total_count=0))
                        room.theatre_unit_id = theatre_unit.id
                        room.name = input_obj.name
                        room.code = input_obj.code
                        room.category = input_obj.category
                        room.capacity = input_obj.capacity
                        room.equipment_notes = input_obj.equipment_notes
                        room.description = input_obj.description
                        if input_obj.status:
                            room.status = input_obj.status
                        if username:
                            room.updated_by = username
                    else:
                        room = TheatreRoom(
                            theatre_unit_id=theatre_unit.id,
                            name=input_obj.name,
                            code=input_obj.code,
                            category=input_obj.category,
                            capacity=input_obj.capacity,
                            equipment_notes=input_obj.equipment_notes,
                            description=input_obj.description,
                            status=input_obj.status or TheatreRoomStatus.OPEN,
                        )
                        if username:
                            room.created_by = username
                            room.updated_by = username
                        session.add(room)

                session.commit()

            return Response(status=True, code=ResponseCode.SUCCESS, message="Theatre room saved successfully",
                            data=TheatreRoomListNode(items=[], total_count=0))
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to save theatre room",
                            data=TheatreRoomListNode(items=[], total_count=0))

    def set_status(self, uid: str, status: TheatreRoomStatus, info: Optional[Info] = None) -> Response[TheatreRoomListNode]:
        try:
            username = self._get_user_name(info)
            with session_scope() as session:
                room = (
                    session.query(TheatreRoom)
                    .filter(TheatreRoom.uid == uid, TheatreRoom.deleted_at.is_(None))
                    .first()
                )
                if not room:
                    return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                    message="Theatre Room not found.",
                                    data=TheatreRoomListNode(items=[], total_count=0))
                room.status = status
                if username:
                    room.updated_by = username
                session.commit()

            return Response(status=True, code=ResponseCode.SUCCESS,
                            message=f"Theatre room marked {status.value.lower()}",
                            data=TheatreRoomListNode(items=[], total_count=0))
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to update theatre room status",
                            data=TheatreRoomListNode(items=[], total_count=0))


TheatreRoomCrud = TheatreRoomService(TheatreRoom)
