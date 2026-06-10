from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class PermissionEnum(str):
    pass


class PermissionResponse(BaseModel):
    user_guid: str
    version: int
    groups: List[str] = []
    permissions: List[str] = []


class TokenPayload(BaseModel):
    guid: str
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    perm_version: int = 0
    department: Optional[str] = None
    directory: Optional[str] = None
    title: Optional[str] = None
    hospital_number: Optional[str] = None


class CurrentUser(BaseModel):
    uid: str
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    groups: List[str] = []
    permissions: List[str] = []
    perm_version: int = 0
    department: Optional[str] = None
    directory: Optional[str] = None
    title: Optional[str] = None
    pf_number: Optional[str] = None
    token: Optional[str] = None

    @property
    def is_admin(self) -> bool:
        return "admin" in (g.lower() for g in self.groups) or "admin" in (p.lower() for p in self.permissions)

    def has_permission(self, perm: str) -> bool:
        return perm in self.permissions

    def has_any_group(self, groups: list[str]) -> bool:
        return any(g in self.groups for g in groups)
