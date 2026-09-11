import strawberry

from src.modules.theatre_time_setting.service import TheatreTimeSettingCrud, _to_node
from src.modules.theatre_time_setting.types import TheatreTimeSettingInput, TheatreTimeSettingNode
from src.shared.response import Response
from src.shared.response_code import ResponseCode

from src.core.security import CustomPermissionExtension, Info


@strawberry.type
class TheatreTimeSettingQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_THEATRE_TIME_SETTINGS"])])
    def get_theatre_time_setting(self) -> Response[TheatreTimeSettingNode]:
        try:
            obj = TheatreTimeSettingCrud.get_current()
            return Response(status=True, code=ResponseCode.SUCCESS, message="Retrieved", data=_to_node(obj))
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=None)


@strawberry.type
class TheatreTimeSettingMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_THEATRE_TIME_SETTINGS"])])
    def save_theatre_time_setting(self, input: TheatreTimeSettingInput, info: Info) -> Response[TheatreTimeSettingNode]:
        try:
            return TheatreTimeSettingCrud.save(input, info=info)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed", data=None)
