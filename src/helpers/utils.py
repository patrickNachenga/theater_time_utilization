import dataclasses
import re
from typing import List

from passlib.context import CryptContext

from src.core.security import Info

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def dataclass_from_dict(klass, d):
    try:
        fieldtypes = {f.name: f.type for f in dataclasses.fields(klass)}
        return klass(**{f: dataclass_from_dict(fieldtypes[f], d[f]) for f in d})
    except:
        return d  # Not a dataclass field


def decode_ldap_attributes(ldap_string):
    return ldap_string[0].decode('ASCII')


def camel_to_snake(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def auth_user_has_permission(info: Info, required_permissions: List[str]):
    """
    Check if login user has supplied permissions
    """
    if info.context.user:
        for perm in required_permissions:
            print(info.context.user.authorities)
            if perm in info.context.user.authorities:
                return True
    return False
