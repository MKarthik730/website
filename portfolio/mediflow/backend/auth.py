# ================================================================
#  auth.py — JWT + bcrypt authentication utilities
# ================================================================

# ── Silence passlib's "(trapped) error reading bcrypt version" ───
# passlib prints this directly via a bare print(), not via the
# warnings module, so warnings.filterwarnings does nothing.
# The real fix is bcrypt==4.0.1 in requirements.txt.
# This monkeypatch covers any environment where an older bcrypt
# slips through — it injects a fake __about__ so passlib never
# hits the except block at all.
import types as _types, sys as _sys
if "bcrypt" not in _sys.modules:
    import bcrypt as _bcrypt_pre
else:
    _bcrypt_pre = _sys.modules["bcrypt"]

if not hasattr(_bcrypt_pre, "__about__"):
    _about = _types.ModuleType("bcrypt.__about__")
    _about.__version__ = getattr(_bcrypt_pre, "__version__", "4.0.1")
    _bcrypt_pre.__about__ = _about

import warnings
warnings.filterwarnings("ignore", message=".*__about__.*")
warnings.filterwarnings("ignore", message=".*bcrypt.*")
# ─────────────────────────────────────────────────────────────────

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY                  = os.getenv("SECRET_KEY", "mediflow-super-secret-key-change-in-prod")
ALGORITHM                   = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS   = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
http_bearer = HTTPBearer(auto_error=True)


# ── Password helpers ─────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT helpers ──────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire  = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    expire  = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail      = "Invalid or expired token",
            headers     = {"WWW-Authenticate": "Bearer"},
        )


# ── FastAPI dependency — extract user from Bearer token ──────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    return payload   # {"sub": username, "role": role, "user_id": id}


# ── Role-based access control ────────────────────────────────────

def require_role(*roles: str):
    """Factory: returns a FastAPI dependency that checks the caller's role."""
    def checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role = current_user.get("role")
        if user_role not in roles:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail      = (
                    f"Access denied. Your role is '{user_role}'. "
                    f"Required: {sorted(roles)}"
                ),
            )
        return current_user
    return checker
