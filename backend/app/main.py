from fastapi import FastAPI, Depends, HTTPException, status # Add status and HTTPException
from fastapi.middleware.cors import CORSMiddleware # Add this import
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session # Add Session

from .database import engine, create_db_and_tables, get_db # Import create_db_and_tables and get_db
from .routers import auth, users, chat, patients # Import the new patients router
from . import models, schemas, crud # Import models, schemas, and crud
from .utils import send_password_reset_email # Import email utility
from datetime import datetime # Import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    create_db_and_tables()
    yield
    # Optional: Add any shutdown logic here

app = FastAPI(
    title="Clinic Management API",
    description="API for Clinic Management, a healthcare access platform for rural communities.",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Middleware configuration
origins = [
    "http://localhost:3000",  # Allow your React frontend
    # You can add other origins here if needed, e.g., your deployed frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(patients.router, prefix="/patients", tags=["Patients"])

@app.post("/password/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    request_data: schemas.ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, email=request_data.email)
    if not user:
        # Avoid leaking information about whether an email exists
        # You might want to log this attempt for security monitoring
        print(f"Password reset attempt for non-existent email: {request_data.email}")
        return {"message": "If an account with that email exists, a password reset link has been sent."}

    token = crud.create_password_reset_token(db, user=user)
    # Ensure user.email is treated as a string
    user_email = str(user.email) if user.email is not None else ""
    if user_email: # Proceed only if email is a valid string
        send_password_reset_email(email=user_email, token=token)
    else:
        # Handle case where user email might be None, though unlikely for an existing user
        print(f"User {user.username} does not have an email address for password reset.")
        # You might want to raise an HTTPException here or return a specific message
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User email not found.")

    return {"message": "If an account with that email exists, a password reset link has been sent."}

@app.post("/password/reset-password", status_code=status.HTTP_200_OK)
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


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Clinic Management API"}