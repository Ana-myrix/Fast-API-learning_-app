import hashlib
import hmac
import secrets


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
    """Store a hash of a reset code, not the code itself."""
    return hashlib.sha256(code.encode()).hexdigest()


def generate_code() -> str:
    """A random 6-digit code, for example '048291'."""
    return f"{secrets.randbelow(1_000_000):06d}"
