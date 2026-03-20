#!/usr/bin/env python3
"""
create_admin.py — Create or reset the admin account.

Usage:
    python create_admin.py                          # interactive
    python create_admin.py --username admin --password yourpass
    python create_admin.py --reset                  # reset existing admin password
"""
import sys, argparse, types as _types

# Patch bcrypt FIRST before passlib loads
try:
    import bcrypt as _b
    if not hasattr(_b, "__about__"):
        _a = _types.ModuleType("bcrypt.__about__")
        _a.__version__ = getattr(_b, "__version__", "4.0.1")
        _b.__about__ = _a
except ImportError:
    pass

import uuid
from mediflow_db.config import engine, SessionLocal
import mediflow_db.models
from mediflow_db.models import UserAuth, RoleEnum
from mediflow_db.config import Base
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def main():
    parser = argparse.ArgumentParser(description="Create or reset MediFlow admin account")
    parser.add_argument("--username", default=None, help="Admin username")
    parser.add_argument("--password", default=None, help="Admin password (min 8 chars)")
    parser.add_argument("--reset",    action="store_true", help="Reset password of existing admin")
    args = parser.parse_args()

    print("\n🔐  MediFlow Admin Setup\n")

    username = args.username or input("Admin username: ").strip()
    password = args.password or input("Admin password (min 8 chars): ").strip()

    if not username or not password:
        print("❌  Username and password are required"); sys.exit(1)
    if len(password) < 8:
        print("❌  Password must be at least 8 characters"); sys.exit(1)

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing_admin = db.query(UserAuth).filter(UserAuth.role == RoleEnum.admin).first()
        existing_user  = db.query(UserAuth).filter(UserAuth.username == username).first()

        if existing_admin and not args.reset:
            # Admin exists — offer to reset password
            print(f"⚠️  An admin already exists: '{existing_admin.username}'")
            if existing_user and existing_user.auth_id == existing_admin.auth_id:
                choice = input(f"Reset password for '{username}'? [y/N]: ").strip().lower()
                if choice == 'y':
                    existing_admin.hashed_password = pwd.hash(password)
                    existing_admin.is_active = True
                    db.commit()
                    print(f"\n✅  Password reset for admin '{username}'")
                    print(f"    → Log in at http://localhost:8000 with these credentials.\n")
                else:
                    print("No changes made.")
            else:
                print(f"   To reset its password run: python create_admin.py --reset --username {existing_admin.username} --password newpass")
            return

        if args.reset:
            # Find existing admin by username and reset
            target = db.query(UserAuth).filter(UserAuth.username == username).first()
            if not target:
                print(f"❌  No user found with username '{username}'"); sys.exit(1)
            target.hashed_password = pwd.hash(password)
            target.role = RoleEnum.admin
            target.is_active = True
            db.commit()
            print(f"\n✅  Password reset for '{username}' (role set to admin)")
            print(f"    → Log in at http://localhost:8000\n")
            return

        # Create fresh admin
        if existing_user:
            print(f"⚠️  Username '{username}' exists with role '{existing_user.role.value}'")
            choice = input(f"Promote '{username}' to admin and reset password? [y/N]: ").strip().lower()
            if choice == 'y':
                existing_user.role = RoleEnum.admin
                existing_user.hashed_password = pwd.hash(password)
                existing_user.is_active = True
                db.commit()
                print(f"\n✅  '{username}' promoted to admin with new password.\n")
            return

        admin = UserAuth(
            user_ref_id     = uuid.uuid4(),
            role            = RoleEnum.admin,
            username        = username,
            hashed_password = pwd.hash(password),
            is_active       = True,
        )
        db.add(admin)
        db.commit()
        print(f"\n✅  Admin account created!")
        print(f"    Username : {username}")
        print(f"    Role     : admin")
        print(f"    → Start the server and log in with these credentials.\n")

    except Exception as e:
        db.rollback()
        print(f"❌  Error: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
