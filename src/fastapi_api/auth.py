import hashlib
import hmac
import secrets
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

# How long a reset code stays valid (10 minutes).
CODE_TTL_SECONDS = 10 * 60
MIN_PASSWORD_LENGTH = 8

# In-memory storage (lost when the server stops). Good enough for learning.
# users:       email -> {"password_hash": "..."}
# reset_codes: email -> {"code_hash": "...", "expires_at": <unix time>}
users: dict[str, dict] = {}
reset_codes: dict[str, dict] = {}


# ---------- helpers ----------

def hash_password(password: str) -> str:
    """Turn a password into a scrambled string that can't be reversed."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt, digest_hex = stored.split("$")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return hmac.compare_digest(digest.hex(), digest_hex)


def hash_code(code: str) -> str:
    """Store a hash of the reset code, not the code itself."""
    return hashlib.sha256(code.encode()).hexdigest()


def generate_code() -> str:
    """A random 6-digit code, e.g. '048291'."""
    return f"{secrets.randbelow(1_000_000):06d}"


# ---------- request bodies ----------

class RegisterRequest(BaseModel):
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str


# ---------- endpoints ----------

@router.post("/register", status_code=201)
def register(body: RegisterRequest):
    email = body.email.lower().strip()
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")
    if len(body.password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters",
        )
    if email in users:
        raise HTTPException(status_code=400, detail="Email already registered")

    users[email] = {"password_hash": hash_password(body.password)}
    return {"message": "User registered", "email": email}


@router.post("/forgot-password")
def forgot_password(body: ForgotPasswordRequest):
    email = body.email.lower().strip()

    # Only create a code if the account exists, but ALWAYS return the same
    # message so people can't use this endpoint to find out who has an account.
    if email in users:
        code = generate_code()
        reset_codes[email] = {
            "code_hash": hash_code(code),
            "expires_at": time.time() + CODE_TTL_SECONDS,
        }
        # Instead of emailing it, print it in the terminal for now.
        print(f"[PASSWORD RESET] Code for {email}: {code} (valid 10 minutes)", flush=True)

    return {"message": "If that email is registered, a reset code has been sent."}


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest):
    email = body.email.lower().strip()
    entry = reset_codes.get(email)

    if (
        entry is None
        or time.time() > entry["expires_at"]
        or not hmac.compare_digest(entry["code_hash"], hash_code(body.code))
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    if len(body.new_password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters",
        )

    users[email]["password_hash"] = hash_password(body.new_password)
    # The code can be used only once.
    del reset_codes[email]
    return {"message": "Password has been reset"}
