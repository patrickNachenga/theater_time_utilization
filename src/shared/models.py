from dataclasses import dataclass
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel


class PermissionDto(BaseModel):
    name: str
    code: str
    service: str
    description: str = None


class StudentPChangeModel(BaseModel):
    registration_number: str = None
    remarks: str = None


@dataclass
class Permission(object):
    name: str
    code: str
    description: str
    service: str


@dataclass
class StudentPChangeModel(object):
    registration_number: str
    remarks: str
    approval_status: str
    f4indexno: str


class AuthorityModel(BaseModel):
    authority: Optional[str] = None


class TokenDetailsModel(BaseModel):
    grant_type: Optional[str] = None
    username: Optional[str] = None


class StudentAuthModel(BaseModel):
    uid: Optional[UUID] = None
    registration_number: Optional[str] = None


class StaffAuthModel(BaseModel):
    uid: Optional[UUID] = None
    pf_number: Optional[str] = None


class UserAuthModel(BaseModel):
    id: Optional[int] = None
    uid: Optional[UUID] = None
    username: Optional[str] = None
    moodle_username: Optional[str] = None
    authorities: Optional[List[str]] = None
    student: Optional[StudentAuthModel] = None
    staff: Optional[StaffAuthModel] = None
    campus_headships: Optional[List[str]] = None
    unit_headships: Optional[List[str]] = None
    department_headships: Optional[List[str]] = None
    program_headships: Optional[List[str]] = None


class UserModel(BaseModel):
    id: Optional[int] = None
    uid: Optional[UUID] = None
    email: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    moodle_id: Optional[int] = None
    moodle_username: Optional[str] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None


class UserHeadshipsModel(BaseModel):
    campus_headships: Optional[List[str]] = None
    unit_headships: Optional[List[str]] = None
    department_headships: Optional[List[str]] = None
    program_headships: Optional[List[str]] = None


class UserAuthenticatedModel(BaseModel):
    authorities: Optional[List[str]] = None
    profile: Optional[UserModel] = None
    headships: Optional[UserHeadshipsModel] = None


class StaffModel(BaseModel):
    uid: Optional[UUID] = None
    user: Optional[UserModel] = None


class StudentModel(BaseModel):
    uid: Optional[UUID] = None
    registration_number: Optional[str] = None
    programme_uid: Optional[str] = None
    bylaw_uid: Optional[str] = None
    status: Optional[str] = None
    user: Optional[UserModel] = None
