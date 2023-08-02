from dataclasses import dataclass
from typing import Optional, List

from pydantic import BaseModel


class PermissionDto(BaseModel):
    name: str
    code: str
    service: str
    description: str = None


@dataclass
class Permission(object):
    name: str
    code: str
    description: str
    service: str


class AuthorityModel(BaseModel):
    authority: Optional[str] = None


class TokenDetailsModel(BaseModel):
    grant_type: Optional[str] = None
    username: Optional[str] = None

#
# class UserAuthenticatedModel(BaseModel):
#     authorities: Optional[List[AuthorityModel]] = None
#     details: Optional[TokenDetailsModel] = None
#     authenticated: Optional[bool] = None
#     credentials: Optional[str] = None
#     name: Optional[str] = None


class UserAuthenticatedModel(BaseModel):
    authorities: Optional[List[str]] = None
    credentials: Optional[str] = None
    name: Optional[str] = None

