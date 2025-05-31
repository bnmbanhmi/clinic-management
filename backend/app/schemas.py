from pydantic import BaseModel, EmailStr, ConfigDict # Add ConfigDict
from typing import Optional, List
from datetime import date, datetime # Added date
from .database import UserRole # Ensure UserRole is available if needed for nested schemas

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

# User Schemas
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: UserRole # UserRole will be updated to PATIENT, DOCTOR, CLINIC_STAFF, ADMIN

class UserCreate(UserBase):
    password: str

class UserCreateInternal(UserCreate): # For internal use, like creating from admin panel
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    # role: UserRole # Already in UserBase

    model_config = ConfigDict(from_attributes=True) # Updated for Pydantic v2

class UserSchema(UserBase): # Renamed from User to UserSchema to avoid conflict with model
    id: int

    model_config = ConfigDict(from_attributes=True) # Updated for Pydantic v2

# Password Recovery Schemas
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# Token Data Schema (for dependency)
class TokenData(BaseModel):
    username: str # Changed from Optional[str] to str
    role: Optional[UserRole] = None # Add role to token data

# Patient Schemas
class PatientBase(BaseModel):
    full_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    emr_summary: Optional[str] = None # Electronic Health Record summary

class PatientCreate(PatientBase):
    user_id: int # Added to link to an existing user
    # creator_id will be set based on the logged-in user (Patient or Clinic Staff)
    assigned_doctor_id: Optional[int] = None # Doctor can be assigned at creation or later

class PatientUpdate(PatientBase):
    full_name: Optional[str] = None # All fields optional for update
    assigned_doctor_id: Optional[int] = None
    # Add other updatable fields as necessary

class PatientSchema(PatientBase):
    id: int
    creator_id: int
    assigned_doctor_id: Optional[int] = None 
    created_at: datetime
    updated_at: datetime
    creator: Optional[UserSchema] = None # Nested schema for creator info
    assigned_doctor: Optional[UserSchema] = None # Nested schema for assigned doctor info.

    model_config = ConfigDict(from_attributes=True) # Updated for Pydantic v2

# Appointment Schemas (New)
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_time: datetime
    reason: Optional[str] = None
    status: Optional[str] = "Scheduled" # e.g., Scheduled, Cancelled, Completed

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    appointment_time: Optional[datetime] = None
    reason: Optional[str] = None
    status: Optional[str] = None

class AppointmentSchema(AppointmentBase):
    id: int
    patient_id: int
    doctor_id: int
    # doctor: UserSchema  # Potentially include doctor details
    # patient: PatientSchema # Potentially include patient details

    model_config = ConfigDict(from_attributes=True) # Updated for Pydantic v2

# New schema for EMR updates
class PatientEMRUpdate(BaseModel):
    emr_summary: Optional[str] = None

class ChatMessageBase(BaseModel):
    message_text: str

class ChatMessageCreate(ChatMessageBase):
    user_id: Optional[int] = None # Optional: Link message to a user if logged in

class ChatMessageSchema(ChatMessageBase):
    id: int
    timestamp: datetime
    response: Optional[str] = None # Chatbot's response
    user_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True) # Updated for Pydantic v2