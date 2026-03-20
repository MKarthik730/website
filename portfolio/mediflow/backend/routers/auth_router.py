# ================================================================
#  routers/auth_router.py
# ================================================================
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import uuid

from mediflow_db.config import get_db
from mediflow_db.models import UserAuth, UserAuthData, LoginResponse, RoleEnum
from auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    get_current_user, require_role,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


# ── Register ─────────────────────────────────────────────────────

@router.post("/register", status_code=201)
def register(data: UserAuthData, db: Session = Depends(get_db)):
    if db.query(UserAuth).filter(UserAuth.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    try:
        ref_id = uuid.UUID(data.user_ref_id) if data.user_ref_id else uuid.uuid4()
    except (ValueError, AttributeError):
        ref_id = uuid.uuid4()

    user = UserAuth(
        user_ref_id     = ref_id,
        role            = data.role,
        username        = data.username,
        hashed_password = hash_password(data.password),
        is_active       = True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "auth_id":   str(user.auth_id),
        "username":  user.username,
        "role":      user.role.value,
        "is_active": user.is_active,
    }


# ── Login ─────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserAuth).filter(UserAuth.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token_data = {
        "sub":     user.username,
        "role":    user.role.value,
        "user_id": str(user.auth_id),
    }
    access_token  = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    user.refresh_token = refresh_token
    db.commit()

    return LoginResponse(
        access_token = access_token,
        token_type   = "bearer",
        user_id      = str(user.auth_id),
        username     = user.username,
        role         = user.role.value,
    )


# ── Refresh ───────────────────────────────────────────────────────

@router.post("/refresh")
def refresh(token: str, db: Session = Depends(get_db)):
    from auth import decode_token
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = db.query(UserAuth).filter(UserAuth.username == payload["sub"]).first()
    if not user or user.refresh_token != token:
        raise HTTPException(status_code=401, detail="Refresh token mismatch")
    new_access = create_access_token({
        "sub":     user.username,
        "role":    user.role.value,
        "user_id": str(user.auth_id),
    })
    return {"access_token": new_access, "token_type": "bearer"}


# ── Me / Whoami ───────────────────────────────────────────────────

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """Returns the decoded JWT payload — useful for debugging role issues."""
    return current_user


@router.get("/whoami")
def whoami(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns full user details including role stored in DB."""
    user = db.query(UserAuth).filter(UserAuth.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in DB")
    return {
        "username":    user.username,
        "role_in_db":  user.role.value,
        "role_in_jwt": current_user.get("role"),
        "roles_match": user.role.value == current_user.get("role"),
        "user_id":     str(user.auth_id),
        "is_active":   user.is_active,
    }


# ── Logout ────────────────────────────────────────────────────────

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(UserAuth).filter(UserAuth.username == current_user["sub"]).first()
    if user:
        user.refresh_token = None
        db.commit()
    return {"message": "Logged out successfully"}


# ── Admin bootstrap (dev only) ────────────────────────────────────

@router.post("/bootstrap-admin", status_code=201, tags=["Dev"])
def bootstrap_admin(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Creates the first admin account. Only works when NO admin exists yet.
    Remove or protect this endpoint in production.
    """
    existing_admin = db.query(UserAuth).filter(UserAuth.role == RoleEnum.admin).first()
    if existing_admin:
        raise HTTPException(
            status_code=409,
            detail=f"An admin already exists: '{existing_admin.username}'. Use /login instead."
        )
    user = UserAuth(
        user_ref_id     = uuid.uuid4(),
        role            = RoleEnum.admin,
        username        = data.username,
        hashed_password = hash_password(data.password),
        is_active       = True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "message":  "Admin account created",
        "username": user.username,
        "role":     user.role.value,
    }


# ── Change role (admin only) ──────────────────────────────────────

@router.patch("/users/{username}/role")
def change_user_role(
    username: str,
    new_role: RoleEnum,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("admin")),
):
    """Lets an admin promote/demote any user's role."""
    user = db.query(UserAuth).filter(UserAuth.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    old_role   = user.role.value
    user.role  = new_role
    db.commit()
    return {
        "username": username,
        "old_role": old_role,
        "new_role": new_role.value,
    }


# ── Reset own password ────────────────────────────────────────────

class PasswordResetRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

@router.post("/reset-password")
def reset_password(
    body: PasswordResetRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lets any logged-in user change their own password."""
    user = db.query(UserAuth).filter(UserAuth.username == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(body.old_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    user.hashed_password = hash_password(body.new_password)
    user.refresh_token = None   # invalidate all existing sessions
    db.commit()
    return {"message": "Password updated. Please log in again."}


# ── Admin force-reset any user's password ─────────────────────────

class AdminPasswordReset(BaseModel):
    new_password: str = Field(..., min_length=8)

@router.patch("/users/{username}/password")
def admin_reset_password(
    username: str,
    body: AdminPasswordReset,
    db: Session = Depends(get_db),
    _: dict = Depends(require_role("admin")),
):
    """Admin can force-reset any user's password."""
    user = db.query(UserAuth).filter(UserAuth.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    user.hashed_password = hash_password(body.new_password)
    user.refresh_token = None
    db.commit()
    return {"message": f"Password reset for '{username}'. They must log in again."}
