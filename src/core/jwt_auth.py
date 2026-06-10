from datetime import timedelta
from typing import Dict

# Support both python-jose and PyJWT de/serializers. Use what's available in the environment.
try:
    from jose import jwt as jose_jwt, JWTError as JoseJWTError, ExpiredSignatureError as JoseExpired
    _HAS_JOSE = True
except Exception:
    _HAS_JOSE = False

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from passlib.context import CryptContext

from src.core.config import settings

ALGORITHM = settings.JWT_ALGORITHM

# Optional expiry settings (fallbacks if not provided)
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, "JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 15)
REFRESH_TOKEN_EXPIRE_MINUTES = getattr(settings, "JWT_REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

# Load RSA public key used to verify incoming JWTs
PUBLIC_KEY_PATH = getattr(settings, "JWT_PUBLIC_KEY_PATH", "public.pem")
try:
    with open(PUBLIC_KEY_PATH, "r") as f:
        PUBLIC_KEY = f.read()
except Exception as e:
    raise Exception(f"Unable to load public key from {PUBLIC_KEY_PATH}: {e}")


async def get_token(token=Depends(bearer_scheme)) -> str:
    """FastAPI dependency to extract bearer token from Authorization header"""
    return str(token.credentials)


def _decode_with_available_lib(token: str, algorithms=[ALGORITHM], audience=None, issuer=None) -> Dict:
    """Decode using python-jose if available, otherwise fallback to PyJWT.

    Raises HTTPException on invalid/expired tokens.
    """
    if _HAS_JOSE:
        try:
            return jose_jwt.decode(token, PUBLIC_KEY, algorithms=algorithms, audience=audience, issuer=issuer)
        except JoseExpired:
            raise HTTPException(status_code=401, detail="Token is expired")
        except JoseJWTError:
            raise HTTPException(status_code=401, detail="Token is invalid")
    else:
        # Fallback to PyJWT (the original code used `import jwt`), which should be present in many environments.
        try:
            import jwt as pyjwt
            from jwt.exceptions import ExpiredSignatureError as PyExpired, InvalidTokenError as PyInvalid
        except Exception:
            raise HTTPException(status_code=500, detail="No JWT library available to validate tokens")

        try:
            return pyjwt.decode(token, key=PUBLIC_KEY, algorithms=algorithms, audience=audience, issuer=issuer)
        except PyExpired:
            raise HTTPException(status_code=401, detail="Token is expired")
        except PyInvalid:
            raise HTTPException(status_code=401, detail="Token is invalid")


def _decode_token(token: str) -> Dict:
    return _decode_with_available_lib(token, algorithms=[ALGORITHM], audience=getattr(settings, "JWT_AUDIENCE", None), issuer=getattr(settings, "JWT_ISSUER", None))


def get_data(token: str) -> Dict:
    """Convenience wrapper used by other modules (raises on invalid tokens)."""
    return _decode_token(token)
