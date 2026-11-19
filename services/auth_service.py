import hmac
import time

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from models.user import ResetCode, User
from services import security
from services.errors import AppError

CODE_TTL_SECONDS = 10 * 60  # reset codes are valid for 10 minutes
MIN_PASSWORD_LENGTH = 8

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo123"


def _normalize_email(email: str) -> str:
    return email.lower().strip()


def _get_user(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def _check_password_length(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AppError(
            400, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
        )


def ensure_demo_user(db: Session) -> None:
    """Create the demo login account if it doesn't exist yet."""
    if _get_user(db, DEMO_EMAIL) is None:
        db.add(
            User(
                email=DEMO_EMAIL,
                password_hash=security.hash_password(DEMO_PASSWORD),
            )
        )
        db.commit()


def register_user(db: Session, email: str, password: str) -> str:
    email = _normalize_email(email)
    if "@" not in email:
        raise AppError(400, "Invalid email address")
    _check_password_length(password)
    if _get_user(db, email) is not None:
        raise AppError(400, "Email already registered")

    db.add(User(email=email, password_hash=security.hash_password(password)))
    db.commit()
    return email


def login(db: Session, email: str, password: str) -> str:
    email = _normalize_email(email)
    user = _get_user(db, email)
    if user is None or not security.verify_password(password, user.password_hash):
        raise AppError(401, "Invalid email or password")
    return email


def request_password_reset(db: Session, email: str) -> None:
    """Create a reset code if the account exists.

    The route always returns the same message, so this never reveals
    which emails are registered.
    """
    user = _get_user(db, _normalize_email(email))
    if user is None:
        return

    # Remove older codes so only the newest one works.
    db.execute(delete(ResetCode).where(ResetCode.user_id == user.id))

    code = security.generate_code()
    db.add(
        ResetCode(
            user_id=user.id,
            code_hash=security.hash_code(code),
            expires_at=time.time() + CODE_TTL_SECONDS,
        )
    )
    db.commit()
    # No email service yet, so the code is printed in the server terminal.
    print(f"[PASSWORD RESET] Code for {user.email}: {code} (valid 10 minutes)", flush=True)


def reset_password(db: Session, email: str, code: str, new_password: str) -> None:
    user = _get_user(db, _normalize_email(email))
    entry = (
        db.scalar(select(ResetCode).where(ResetCode.user_id == user.id))
        if user is not None
        else None
    )

    if (
        entry is None
        or time.time() > entry.expires_at
        or not hmac.compare_digest(entry.code_hash, security.hash_code(code))
    ):
        raise AppError(400, "Invalid or expired code")

    _check_password_length(new_password)
    user.password_hash = security.hash_password(new_password)
    db.delete(entry)  # a code can be used only once
    db.commit()
