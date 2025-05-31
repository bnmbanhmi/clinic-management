from fastapi import APIRouter, Depends, HTTPException, status, Security, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List

from app import crud, models, schemas
from app.database import get_db
from app.config import settings
from app.dependencies import get_current_user # Assuming get_current_user is here

# OAuth2 and Password Hashing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# get_current_active_user moved to dependencies.py

# Router for authentication
router = APIRouter()

@router.post("/token", response_model=schemas.Token, tags=["authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Authenticate using email (which is in form_data.username as per OAuth2PasswordRequestForm)
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Include user's role in the token data
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value}, expires_delta=access_token_expires # Use .value for Enum
    )
    # Return role and user_id in the response body along with the token
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        # "role": user.role.value, # Role is in the token, not directly in Token schema
        # "user_id": user.id # User ID also not directly in Token schema
    }

@router.post("/register/", response_model=schemas.UserSchema, tags=["authentication"])
async def register_user(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    if body:
        print(f"Received user data: {body}")
    else:
        print("No user data received")
        raise HTTPException(status_code=400, detail="Do not receive user data")
    
    user = schemas.UserCreate(username=body['username'],
                              email=body['email'],  # Using email as username for registration
                              full_name=body['full_name'],
                              password=body['password'],
                              role=models.UserRole.PATIENT)
    try:
        email = user.email.lower()
        username = user.username.lower()
        full_name = user.full_name.strip() if user.full_name else None
        password = user.password
        print(f"Registering user: {username}, email: {email}, full_name: {full_name}, password: {password}")
    except AttributeError as e:
        raise HTTPException(status_code=400, detail="Invalid user data format") from e


    if not user.email:
        raise HTTPException(status_code=400, detail="Email is required for registration")

    if crud.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    if crud.get_user_by_username(db, username=user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    return crud.create_user(db=db, user=user)