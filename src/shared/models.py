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
    """Model for user data returned from JWT token or Auth Service"""
    id: Optional[int] = None
    full_name: Optional[str] = None
    uid: Optional[UUID] = None
    username: Optional[str] = None
    email: Optional[str] = None
    pf_number: Optional[str] = None
    authorities: Optional[List[str]] = None
    groups: Optional[List[str]] = None
    perm_version: Optional[int] = None
    department: Optional[str] = None
    department_uid: Optional[str] = None
    directory: Optional[str] = None
    directory_uid: Optional[str] = None
    phone_number: Optional[List[str]] = None
    guid: Optional[str] = None


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


# ─── Auth / Permission Models ───────────────────────────────────────────────

class TokenPayload(BaseModel):
    """Payload extracted from the decoded JWT token"""
    token_type: Optional[str] = None
    sub: Optional[str] = None
    guid: Optional[str] = None
    pf_number: Optional[str] = None
    hospital_number: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    groups: Optional[List[str]] = None
    perm_version: Optional[int] = None
    iss: Optional[str] = None
    aud: Optional[str] = None
    department: Optional[str] = None
    directory: Optional[str] = None
    title: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None


class PermissionResponse(BaseModel):
    """Response from Auth Service containing user permissions and info"""
    id: Optional[int] = None
    user_guid: Optional[str] = None
    version: Optional[int] = None
    groups: Optional[List[str]] = None
    permissions: Optional[List[str]] = None
    full_name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    pf_number: Optional[str] = None
    department: Optional[str] = None
    department_uid: Optional[str] = None
    directory: Optional[str] = None
    directory_uid: Optional[str] = None


class CurrentUser(BaseModel):
    """Model representing the authenticated user with resolved permissions.
    
    Mirrors all fields from PermissionResponse plus token.
    This is the primary user context used throughout the application.
    """
    id: Optional[str] = None
    uid: Optional[str] = None
    guid: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    groups: Optional[List[str]] = None
    perm_version: Optional[int] = None
    permissions: Optional[List[str]] = None
    pf_number: Optional[str] = None
    department: Optional[str] = None
    department_uid: Optional[str] = None
    directory: Optional[str] = None
    directory_uid: Optional[str] = None
    token: Optional[str] = None

    @property
    def is_admin(self) -> bool:
        """Check if user has admin group"""
        if not self.groups:
            return False
        return any(g.lower() == "admin" for g in self.groups)

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        if self.is_admin:
            return True
        if not self.permissions:
            return False
        return permission in self.permissions

    def has_any_group(self, groups: List[str]) -> bool:
        """Check if user belongs to any of the given groups"""
        if self.is_admin:
            return True
        if not self.groups:
            return False
        return any(g in self.groups for g in groups)