from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.database import get_db
from schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    email = auth_service.register_user(db, body.email, body.password)
    return {"message": "User registered", "email": email}


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    email = auth_service.login(db, body.email, body.password)
    return {"message": f"Welcome, {email}!", "email": email}


@router.post("/forgot-password")
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    auth_service.request_password_reset(db, body.email)
    # Same message whether or not the email is registered.
    return {"message": "If that email is registered, a reset code has been sent."}


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    auth_service.reset_password(db, body.email, body.code, body.new_password)
    return {"message": "Password has been reset"}
