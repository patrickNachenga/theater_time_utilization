from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID

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


class UserModel(BaseModel):
    uid: Optional[UUID] = None
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    moodle_id: Optional[int] = None


class UserHeadshipsModel(BaseModel):
    campus_headships: Optional[List[str]] = None
    unit_headships: Optional[List[str]] = None
    department_headships: Optional[List[str]] = None
    program_headships: Optional[List[str]] = None


class UserAuthenticatedModel(BaseModel):
    authorities: Optional[List[str]] = None
    profile: Optional[UserModel] = None
    headships: Optional[UserHeadshipsModel] = None
