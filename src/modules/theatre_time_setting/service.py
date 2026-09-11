from datetime import datetime
from typing import Optional

from src.core.security import Info
from src.database.session import session_scope
from src.modules import CRUDBase
from src.models import TheatreTimeSetting
from src.modules.theatre_time_setting.types import TheatreTimeSettingInput, TheatreTimeSettingNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode


def _to_node(obj: Optional[TheatreTimeSetting]) -> Optional[TheatreTimeSettingNode]:
    if not obj:
        return None
    return TheatreTimeSettingNode(
        uid=str(obj.uid),
        start_cutting_time=obj.start_cutting_time.strftime("%H:%M"),
        room_preparation_minutes=obj.room_preparation_minutes,
        patient_induction_minutes=obj.patient_induction_minutes,
    )


class TheatreTimeSettingService(CRUDBase[TheatreTimeSetting, TheatreTimeSettingInput, TheatreTimeSettingInput]):
    def get_current(self) -> Optional[TheatreTimeSetting]:
        """
        The system keeps a single active timing configuration (a settings
        singleton) rather than per-theatre-unit rows, matching how the
        register form only needs one global start-cutting-time reference.
        """
        with session_scope() as session:
            return (
                session.query(TheatreTimeSetting)
                .filter(TheatreTimeSetting.deleted_at.is_(None))
                .order_by(TheatreTimeSetting.id.desc())
                .first()
            )

    def save(self, input_obj: TheatreTimeSettingInput, info: Optional[Info] = None) -> Response[TheatreTimeSettingNode]:
        try:
            username = self._get_user_name(info)
            start_cutting_time = datetime.strptime(input_obj.start_cutting_time, "%H:%M").time()

            with session_scope() as session:
                existing = (
                    session.query(TheatreTimeSetting)
                    .filter(TheatreTimeSetting.deleted_at.is_(None))
                    .order_by(TheatreTimeSetting.id.desc())
                    .first()
                )

                if existing:
                    existing.start_cutting_time = start_cutting_time
                    existing.room_preparation_minutes = input_obj.room_preparation_minutes
                    existing.patient_induction_minutes = input_obj.patient_induction_minutes
                    if username:
                        existing.updated_by = username
                    session.add(existing)
                    obj = existing
                else:
                    obj = TheatreTimeSetting(
                        start_cutting_time=start_cutting_time,
                        room_preparation_minutes=input_obj.room_preparation_minutes,
                        patient_induction_minutes=input_obj.patient_induction_minutes,
                    )
                    if username:
                        obj.created_by = username
                    session.add(obj)

                session.commit()
                session.refresh(obj)

                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Theatre time settings saved successfully",
                    data=_to_node(obj),
                )
        except ValueError:
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Start cutting time must be in HH:MM format",
                data=None,
            )
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to save settings", data=None)


TheatreTimeSettingCrud = TheatreTimeSettingService(TheatreTimeSetting)
