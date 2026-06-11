import logging
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

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
from src.shared.models import TokenPayload

logger = logging.getLogger(__name__)

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


@dataclass
class DecodeResult:
    """Result of JWT decode attempt."""
    success: bool
    payload: Optional[Dict] = None
    error_message: Optional[str] = None


async def get_token(token=Depends(bearer_scheme)) -> str:
    """FastAPI dependency to extract bearer token from Authorization header"""
    return str(token.credentials)


def _decode_with_available_lib(
    token: str,
    algorithms: Optional[list] = None,
    audience: Optional[str] = None,
    issuer: Optional[str] = None,
) -> DecodeResult:
    """Decode using python-jose if available, otherwise fallback to PyJWT.

    Returns DecodeResult — no exceptions raised.
    """
    if algorithms is None:
        algorithms = [ALGORITHM]

    if _HAS_JOSE:
        try:
            payload = jose_jwt.decode(token, PUBLIC_KEY, algorithms=algorithms, audience=audience, issuer=issuer)
            return DecodeResult(success=True, payload=payload)
        except JoseExpired:
            return DecodeResult(success=False, error_message="Token is expired")
        except JoseJWTError as e:
            return DecodeResult(success=False, error_message=f"Token is invalid: {str(e)}")
    else:
        # Fallback to PyJWT
        try:
            import jwt as pyjwt
            from jwt.exceptions import ExpiredSignatureError as PyExpired, InvalidTokenError as PyInvalid
        except Exception:
            return DecodeResult(success=False, error_message="No JWT library available to validate tokens")

        try:
            payload = pyjwt.decode(token, key=PUBLIC_KEY, algorithms=algorithms, audience=audience, issuer=issuer)
            return DecodeResult(success=True, payload=payload)
        except PyExpired:
            return DecodeResult(success=False, error_message="Token is expired")
        except PyInvalid as e:
            return DecodeResult(success=False, error_message=f"Token is invalid: {str(e)}")


def _decode_token(token: str) -> Dict:
    """
    Legacy: Decode JWT and return dict payload.
    Raises HTTPException on failure (for FastAPI dependency use).
    """
    result = _decode_with_available_lib(
        token,
        algorithms=settings.JWT_ALGORITHM,
        audience=settings.JWT_AUDIENCE,
        issuer=settings.JWT_ISSUER,
    )
    if not result.success:
        raise HTTPException(status_code=401, detail=result.error_message)
    return result.payload


def get_data(token: str) -> Dict:
    """Convenience wrapper used by other modules (raises HTTPException on invalid tokens)."""
    return _decode_token(token)


# ─── Safe Decode (returns None instead of raising) ──────────────────────────


def decode_token_payload(token: str) -> Optional[TokenPayload]:
    """
    Safely decode a JWT token and return a TokenPayload model.

    Returns None if the token is invalid, expired, or any other error occurs.
    Used by the Context class in security.py to gracefully handle unauthenticated users.
    """
    result = _decode_with_available_lib(
        token,
        algorithms=settings.JWT_ALGORITHM,
        audience=settings.JWT_AUDIENCE,
        issuer=settings.JWT_ISSUER,
    )

    if not result.success:
        logger.warning(f"JWT decode failed: {result.error_message}")
        return None

    try:
        return TokenPayload(**result.payload)
    except Exception as e:
        logger.error(f"Unexpected error mapping JWT payload to TokenPayload: {e}")
        return None