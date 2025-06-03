from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.database import get_db
from typing import List

from .utils import send_password_reset_email # Import email utility
from datetime import datetime # Import datetime

router = APIRouter(
    tags=["Password"],
    responses={404: {"description": "Not found"}},
)

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request_data: schemas.ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    return {"message": "It seems the 'users' table does not have a 'reset_password_token' column."}
    user = crud.get_user_by_email(db, email=request_data.email)
    if not user:
        # Avoid leaking information about whether an email exists
        # You might want to log this attempt for security monitoring
        print(f"Password reset attempt for non-existent email: {request_data.email}")
        return {"message": "The account with that email doesn't exists"}

    #token = crud.create_password_reset_token(db, user=user)
    # Ensure user.email is treated as a string
    user_email = str(user.email) if user.email is not None else ""
    if user_email: # Proceed only if email is a valid string
        print("send password reset link successfully")
        #send_password_reset_email(email=user_email, token=token)
    else:
        # Handle case where user email might be None, though unlikely for an existing user
        print(f"User {user.username} does not have an email address for password reset.")
        # You might want to raise an HTTPException here or return a specific message
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User email not found.")

    return {"message": "If an account with that email exists, a password reset link has been sent."}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password_route(
    request_data: schemas.ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_reset_token(db, token=request_data.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )
    
    # Ensure user.reset_password_token_expires_at is a datetime object for comparison
    token_expires_at = getattr(user, 'reset_password_token_expires_at', None)
    if not isinstance(token_expires_at, datetime):
        # This case should ideally not happen if data is consistent
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid token expiration data.",
        )

    if token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired.",
        )

    crud.reset_password(db, user=user, new_password=request_data.new_password)
    return {"message": "Password has been reset successfully."}