from sqlalchemy.orm import Session
from typing import Optional # Added Optional
from . import models, schemas # Updated to schemas
from .database import pwd_context, UserRole # Add this import
import secrets
from datetime import datetime, timedelta

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str): # Added for login and other purposes
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100): # Added
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate): # Changed from UserCreateInternal if it was, ensure UserCreate is used
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        hashed_password = pwd_context.hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"] # Ensure plain password is not stored
    else: # remove password from update_data if it is None or empty
        if "password" in update_data:
            del update_data["password"]


    for key, value in update_data.items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_password_reset_token(db: Session, user: models.User) -> str:
    token = secrets.token_urlsafe(32)
    expires_delta = timedelta(hours=1) # Token valid for 1 hour
    expires_at = datetime.utcnow() + expires_delta
    setattr(user, 'reset_password_token', token)
    setattr(user, 'reset_password_token_expires_at', expires_at)
    db.commit()
    db.refresh(user)
    return token

def get_user_by_reset_token(db: Session, token: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.reset_password_token == token).first()

def reset_password(db: Session, user: models.User, new_password: str) -> bool:
    setattr(user, 'hashed_password', pwd_context.hash(new_password))
    setattr(user, 'reset_password_token', None) # Invalidate the token
    setattr(user, 'reset_password_token_expires_at', None)
    db.commit()
    return True

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None

    # If the user is a doctor, nullify their assignment in Patient records
    # Compare the string value of the role stored in the DB
    if str(db_user.role) == UserRole.DOCTOR.value:
        db.query(models.Patient).filter(models.Patient.assigned_doctor_id == user_id).update({models.Patient.assigned_doctor_id: None}, synchronize_session=False)

    # Nullify creator_id in Patient records where this user is the creator
    db.query(models.Patient).filter(models.Patient.creator_id == user_id).update({models.Patient.creator_id: None}, synchronize_session=False)

    db.delete(db_user)
    db.commit()
    return db_user

# Patient CRUD operations
def get_patient(db: Session, patient_id: int):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Patient).offset(skip).limit(limit).all()

def get_patients_by_doctor(db: Session, doctor_id: int, skip: int = 0, limit: int = 100): # Renamed and updated
    return db.query(models.Patient).filter(models.Patient.assigned_doctor_id == doctor_id).offset(skip).limit(limit).all()

def get_patient_by_user_id(db: Session, user_id: int) -> Optional[models.Patient]:
    """Retrieve a patient by their associated user_id."""
    return db.query(models.Patient).filter(models.Patient.user_id == user_id).first()

def create_patient(db: Session, patient_in: schemas.PatientCreate, creator_id: int) -> models.Patient:
    # Selectively create the patient data for the model
    # Fields from PatientCreate that are in Patient model: user_id, gender, emr_summary, assigned_doctor_id
    # Fields like full_name, date_of_birth, address, phone_number are in PatientBase but not Patient model.
    # These details are expected to be on the linked User model.
    # Patient model also has 'age' and 'medical_history' which are not in PatientCreate.
    # These would need to be added to PatientCreate or updated separately if they are to be set at creation.

    patient_data_for_model = {
        "user_id": patient_in.user_id,
        "gender": patient_in.gender, # This comes from PatientBase
        "emr_summary": patient_in.emr_summary, # This comes from PatientBase
        "assigned_doctor_id": patient_in.assigned_doctor_id, # This comes from PatientCreate
        "creator_id": creator_id
    }
    
    # Optional fields: if not provided in patient_in, they might be None.
    # SQLAlchemy handles None for nullable fields. If a field is not nullable and has no default,
    # it must be provided.

    db_patient = models.Patient(**patient_data_for_model)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: int, patient_update: schemas.PatientUpdate) -> Optional[models.Patient]:
    db_patient = get_patient(db, patient_id=patient_id)
    if db_patient:
        update_data = patient_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_patient, key, value)
        db.commit()
        db.refresh(db_patient)
    return db_patient

# Simplified to only update EMR summary
def update_patient_emr(db: Session, patient_id: int, emr_summary: str) -> Optional[models.Patient]:
    """Updates only the EMR summary for a given patient."""
    db_patient = get_patient(db, patient_id=patient_id)
    if db_patient:
        # Use setattr to avoid direct type issues if emr_summary is a Column object to the type checker
        setattr(db_patient, 'emr_summary', emr_summary)
        db.commit()
        db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int):
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None
    db.delete(db_patient)
    db.commit()
    return db_patient

# Appointment CRUD Operations (New)
def create_appointment(db: Session, appointment: schemas.AppointmentCreate, creator_id: int):
    # Assuming creator_id is the ID of the user creating the appointment (Patient or Clinic Staff)
    # The appointment schema itself contains patient_id and doctor_id
    db_appointment = models.Appointment(**appointment.model_dump(), created_by_user_id=creator_id) # Assuming a created_by_user_id field in Appointment model
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_appointment(db: Session, appointment_id: int):
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

def get_appointments_for_patient(db: Session, patient_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).offset(skip).limit(limit).all()

def get_appointments_for_doctor(db: Session, doctor_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Appointment).filter(models.Appointment.doctor_id == doctor_id).offset(skip).limit(limit).all()

def update_appointment(db: Session, appointment_id: int, appointment_update: schemas.AppointmentUpdate):
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
    update_data = appointment_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_appointment, key, value)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def delete_appointment(db: Session, appointment_id: int):
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
    db.delete(db_appointment)
    db.commit()
    return db_appointment

# Chat Message CRUD Operations (New - Basic)
def create_chat_message(db: Session, message: schemas.ChatMessageCreate, user_id: Optional[int] = None): # user_id from current_user
    db_message = models.ChatMessage(**message.model_dump(), user_id=user_id) # Assuming ChatMessage model has user_id
    # Add logic for chatbot response if synchronous, or handle asynchronously
    # For now, just saving the user's message
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_message(db: Session, message_id: int):
    return db.query(models.ChatMessage).filter(models.ChatMessage.id == message_id).first()

def get_chat_messages_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    # This would fetch messages initiated by or involving the user.
    # The exact filter might depend on how conversations are structured.
    return db.query(models.ChatMessage).filter(models.ChatMessage.user_id == user_id).order_by(models.ChatMessage.timestamp.desc()).offset(skip).limit(limit).all()

# Placeholder for a function to get all messages in a conversation (if applicable)
# def get_conversation_messages(db: Session, conversation_id: int, skip: int = 0, limit: int = 100):
#     pass

# Placeholder for a function to add chatbot's response to a message
# def add_chatbot_response_to_message(db: Session, message_id: int, response_text: str):
#     db_message = get_chat_message(db, message_id)
#     if db_message:
#         db_message.response = response_text
#         db.commit()
#         db.refresh(db_message)
#     return db_message