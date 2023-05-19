# from fastapi import APIRouter
# from strawberry.fastapi import BaseContext
# from strawberry.types import Info as _Info
# from strawberry.types.info import RootValueType
# from strawberry.utils.cached_property import cached_property
#
# from src.core.jwt_auth import get_data
# from src.models import User
#
# route = APIRouter()
#
#
# class Context(BaseContext):
#     @cached_property
#     async def user(self) -> User | None:
#         """
#             Get User From Token
#         :return:
#         """
#         if not self.request:
#             return None
#         authorization = self.request.headers.get("Authorization", None)
#
#         from src.modules.users import UserService
#         if authorization:
#             user_data = await get_data(authorization.split(" ")[1])
#             user = UserService().get_user_by_email(user_data.get('username'))
#             return user
#         if self.request.get("access_token"):
#             print(self.request.get("access_token"))
#             user_data = await get_data(self.request.get("access_token"))
#             user = UserService().get_user_by_email(user_data.get('username'))
#             return user
#         return None
#
#
# Info = _Info[Context, RootValueType]
#
#
# async def get_context() -> Context:
#     return Context()
