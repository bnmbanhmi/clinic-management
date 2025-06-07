"""
CRUD Operations for Clinic Management System

This module contains all database CRUD operations for:
- Users (authentication and user management)
- Patients (patient records and management)
- Doctors (doctor profiles and assignments)
- Appointments (scheduling and management)
- Hospitals (hospital information)
- Chat Messages (chatbot interactions)
- Medical Reports (patient medical records)
"""

import secrets
from datetime import datetime, timedelta, time, date
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from . import models, schemas
from .database import pwd_context, UserRole, Class, Gender

# ============================================================================
# USER CRUD OPERATIONS
# ============================================================================

def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Retrieve a user by user ID."""
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Retrieve a user by email address. Used for login and authentication."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Retrieve a user by username."""
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Retrieve all users with pagination."""
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Create a new user and associated role-specific record.
    
    This function handles the creation of both the user account and the
    corresponding role-specific record (Patient, Doctor, or Clinic Staff).
    """
    try:
        # Hash the password and create user record
        hashed_password = pwd_context.hash(user.password)
        db_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            role=user.role,
            full_name=user.full_name
        )
        db.add(db_user)
        db.flush()  # Get db_user.user_id without committing yet
        db.refresh(db_user)  # Refresh to ensure all attributes are populated

        # Extract values using getattr to resolve type checker issues
        user_id_value = getattr(db_user, 'user_id', 0)
        full_name_value = getattr(db_user, 'full_name', 'Unknown')

        # Create role-specific records based on user role
        if user.role == "PATIENT":
            patient_in = schemas.PatientCreate(
                patient_id=user_id_value,  # Use user_id as patient_id for linking
                user_id=user_id_value,     # Link to User table
                full_name=full_name_value,  # Required field from PatientBase
                date_of_birth=date(2000, 1, 1),  # Default date
                gender=Gender.MALE.value,  # Use Gender enum value
                address="",  # Default empty address
                phone_number="",  # Default empty phone (correct field name)
                assigned_doctor_id=None  # No doctor assigned initially
            )
            create_patient(db=db, patient_in=patient_in, creator_id=user_id_value)

        elif user.role == "DOCTOR":
            doctor_in = schemas.DoctorCreate(
                doctor_id=user_id_value,
                doctor_name=full_name_value,
                hospital_id=1  # TODO: Make this configurable instead of hardcoded
            )
            create_doctor(db=db, doctor_in=doctor_in, creator_id=user_id_value)

        elif user.role == "CLINIC_STAFF":
            # No additional records needed for clinic staff currently
            pass

        db.commit()
        db.refresh(db_user)

        print(f"User created successfully: ID={db_user.user_id}, Name={db_user.full_name}, Role={db_user.role}")
        return db_user

    except Exception as e:
        db.rollback()
        print(f"Failed to create user and associated record: {str(e)}")
        raise


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update an existing user's information."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Handle password update with proper hashing
    if "password" in update_data and update_data["password"]:
        hashed_password = pwd_context.hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]  # Remove plain password from update data
    else:
        # Remove empty password field from update data
        if "password" in update_data:
            del update_data["password"]

    # Apply updates to user object
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> Optional[models.User]:
    """
    Delete a user and handle cascade relationships.
    
    When deleting a doctor, their assignment in patient records is nullified.
    """
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        return None

    # Handle doctor deletion - nullify their assignment in patient records
    if str(db_user.role) == UserRole.DOCTOR.value:
        db.query(models.Patient).filter(
            models.Patient.assigned_doctor_id == user_id
        ).update(
            {models.Patient.assigned_doctor_id: None}, 
            synchronize_session=False
        )

    db.delete(db_user)
    db.commit()
    return db_user


# Password Reset Operations
def create_password_reset_token(db: Session, user: models.User) -> str:
    """Generate and store a password reset token for a user."""
    token = secrets.token_urlsafe(32)
    expires_delta = timedelta(hours=1)  # Token valid for 1 hour
    expires_at = datetime.utcnow() + expires_delta
    
    setattr(user, 'reset_password_token', token)
    setattr(user, 'reset_password_token_expires_at', expires_at)
    
    db.commit()
    db.refresh(user)
    return token


def get_user_by_reset_token(db: Session, token: str) -> Optional[models.User]:
    """Retrieve a user by their password reset token."""
    return db.query(models.User).filter(models.User.reset_password_token == token).first()


def reset_password(db: Session, user: models.User, new_password: str) -> bool:
    """Reset a user's password and invalidate the reset token."""
    setattr(user, 'hashed_password', pwd_context.hash(new_password))
    setattr(user, 'reset_password_token', None)  # Invalidate the token
    setattr(user, 'reset_password_token_expires_at', None)
    
    db.commit()
    return True


# ============================================================================
# PATIENT CRUD OPERATIONS
# ============================================================================

def get_patient(db: Session, patient_id: int) -> Optional[models.Patient]:
    """Retrieve a patient by patient ID."""
    return db.query(models.Patient).filter(models.Patient.patient_id == patient_id).first()


def get_patients(db: Session, skip: int = 0, limit: int = 100) -> List[models.Patient]:
    """Retrieve all patients with pagination."""
    return db.query(models.Patient).offset(skip).limit(limit).all()


def get_patients_by_doctor(db: Session, doctor_id: int, skip: int = 0, limit: int = 100) -> List[models.Patient]:
    """Retrieve all patients assigned to a specific doctor."""
    return db.query(models.Patient).filter(
        models.Patient.assigned_doctor_id == doctor_id
    ).offset(skip).limit(limit).all()


def get_patient_by_user_id(db: Session, user_id: int) -> Optional[models.Patient]:
    """Retrieve a patient by their associated user ID."""
    return db.query(models.Patient).filter(models.Patient.patient_id == user_id).first()


def create_patient(db: Session, patient_in: schemas.PatientCreate, creator_id: int) -> models.Patient:
    """
    Create a new patient record.
    
    Note: Some fields like full_name, date_of_birth, etc. are expected to be
    in the linked User model, while patient-specific fields are stored here.
    """
    patient_data = {
        "patient_id": patient_in.patient_id,
        "full_name": patient_in.full_name,
        "date_of_birth": patient_in.date_of_birth or date(2000, 1, 1),
        "gender": patient_in.gender or Gender.MALE,
        "class_role": Class.OTHER,
        "assigned_doctor_id": patient_in.assigned_doctor_id
    }
    
    db_patient = models.Patient(**patient_data)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def update_patient(db: Session, patient_id: int, patient_update: schemas.PatientUpdate) -> Optional[models.Patient]:
    """Update an existing patient's information."""
    db_patient = get_patient(db, patient_id=patient_id)
    if not db_patient:
        return None
    
    update_data = patient_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)
    
    db.commit()
    db.refresh(db_patient)
    return db_patient


def update_patient_emr(db: Session, patient_id: int, emr_summary: str) -> Optional[models.Patient]:
    """Update only the EMR summary for a patient."""
    db_patient = get_patient(db, patient_id=patient_id)
    if not db_patient:
        return None
    
    setattr(db_patient, 'emr_summary', emr_summary)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def delete_patient(db: Session, patient_id: int) -> Optional[models.Patient]:
    """Delete a patient record."""
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None
    
    db.delete(db_patient)
    db.commit()
    return db_patient


def search_patients(
    db: Session, 
    search_params: schemas.PatientSearchQuery, 
    current_user_role: str,
    current_user_id: int
) -> tuple[List[models.Patient], int]:
    """
    Advanced patient search with multiple filters and role-based access control.
    
    Returns:
        tuple: (list_of_patients, total_count)
    """
    from sqlalchemy import and_, or_, func, desc, asc
    from datetime import date
    
    # Base query with joins
    query = db.query(models.Patient).join(
        models.User, models.Patient.patient_id == models.User.user_id
    ).outerjoin(
        models.Doctor, models.Patient.assigned_doctor_id == models.Doctor.doctor_id
    )
    
    # Role-based access control
    if current_user_role == UserRole.DOCTOR.value:
        # Doctors can only see their assigned patients
        query = query.filter(models.Patient.assigned_doctor_id == current_user_id)
    elif current_user_role == UserRole.PATIENT.value:
        # Patients can only see their own record
        query = query.filter(models.Patient.patient_id == current_user_id)
    # ADMIN and CLINIC_STAFF can see all patients (no additional filter)
    
    # Build search conditions
    conditions = []
    
    # General search query (searches across multiple fields)
    if search_params.query:
        search_term = f"%{search_params.query}%"
        general_search = or_(
            models.Patient.full_name.ilike(search_term),
            models.User.email.ilike(search_term),
            models.Patient.phone_number.ilike(search_term),
            models.Patient.identification_id.ilike(search_term),
            models.Patient.health_insurance_card_no.ilike(search_term)
        )
        conditions.append(general_search)
    
    # Specific field searches
    if search_params.patient_id:
        conditions.append(models.Patient.patient_id == search_params.patient_id)
    
    if search_params.full_name:
        conditions.append(models.Patient.full_name.ilike(f"%{search_params.full_name}%"))
    
    if search_params.phone_number:
        conditions.append(models.Patient.phone_number.ilike(f"%{search_params.phone_number}%"))
    
    if search_params.email:
        conditions.append(models.User.email.ilike(f"%{search_params.email}%"))
    
    if search_params.identification_id:
        conditions.append(models.Patient.identification_id.ilike(f"%{search_params.identification_id}%"))
    
    if search_params.health_insurance_card_no:
        conditions.append(models.Patient.health_insurance_card_no.ilike(f"%{search_params.health_insurance_card_no}%"))
    
    if search_params.assigned_doctor_id:
        conditions.append(models.Patient.assigned_doctor_id == search_params.assigned_doctor_id)
    
    if search_params.gender:
        conditions.append(models.Patient.gender == search_params.gender)
    
    # Age filters (calculate age from date_of_birth)
    if search_params.age_min or search_params.age_max:
        today = date.today()
        
        if search_params.age_min:
            max_birth_date = date(today.year - search_params.age_min, today.month, today.day)
            conditions.append(models.Patient.date_of_birth <= max_birth_date)
        
        if search_params.age_max:
            min_birth_date = date(today.year - search_params.age_max - 1, today.month, today.day)
            conditions.append(models.Patient.date_of_birth > min_birth_date)
    
    # Apply all conditions
    if conditions:
        query = query.filter(and_(*conditions))
    
    # Get total count before pagination
    total_count = query.count()
    
    # Sorting
    sort_by = search_params.sort_by or "full_name"
    if hasattr(models.Patient, sort_by):
        sort_field = getattr(models.Patient, sort_by)
    else:
        sort_field = models.Patient.full_name
        
    if search_params.sort_order == "desc":
        query = query.order_by(desc(sort_field))
    else:
        query = query.order_by(asc(sort_field))
    
    # Pagination
    patients = query.offset(search_params.skip).limit(search_params.limit).all()
    
    return patients, total_count


def get_patient_search_result(db: Session, patient: models.Patient) -> schemas.PatientSearchResult:
    """
    Convert a Patient model to PatientSearchResult schema with additional computed fields.
    """
    from datetime import date
    
    # Calculate age
    age = None
    if hasattr(patient, 'date_of_birth') and patient.date_of_birth is not None:
        today = date.today()
        birth_date = patient.date_of_birth
        age = today.year - birth_date.year
        if today.month < birth_date.month or (
            today.month == birth_date.month and today.day < birth_date.day
        ):
            age -= 1
    
    # Get assigned doctor name
    assigned_doctor_name = None
    assigned_doctor_id = getattr(patient, 'assigned_doctor_id', None)
    if assigned_doctor_id is not None:
        doctor = get_doctor(db, assigned_doctor_id)
        if doctor:
            assigned_doctor_name = getattr(doctor, 'doctor_name', None)
    
    # Get user email
    patient_id = getattr(patient, 'patient_id')
    user = get_user(db, patient_id)
    email = getattr(user, 'email', None) if user else None
    
    # Get gender value
    gender_value = None
    if hasattr(patient, 'gender') and patient.gender is not None:
        gender_value = patient.gender.value if hasattr(patient.gender, 'value') else str(patient.gender)
    
    return schemas.PatientSearchResult(
        patient_id=getattr(patient, 'patient_id'),
        full_name=getattr(patient, 'full_name'),
        date_of_birth=getattr(patient, 'date_of_birth', None),
        gender=gender_value,
        phone_number=getattr(patient, 'phone_number', None),
        email=email,
        identification_id=getattr(patient, 'identification_id', None),
        health_insurance_card_no=getattr(patient, 'health_insurance_card_no', None),
        assigned_doctor_id=assigned_doctor_id,
        assigned_doctor_name=assigned_doctor_name,
        age=age
    )

# ============================================================================
# APPOINTMENT CRUD OPERATIONS
# ============================================================================

def create_appointment(db: Session, appointment: schemas.AppointmentCreate, creator_id: int) -> models.Appointment:
    """Create a new appointment."""
    appointment_data = appointment.model_dump()
    appointment_data["patient_id"] = creator_id
    
    db_appointment = models.Appointment(**appointment_data)
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    print(f"Appointment created: {db_appointment}")
    return db_appointment


def get_appointment(db: Session, appointment_id: int) -> Optional[models.Appointment]:
    """Retrieve an appointment by ID."""
    return db.query(models.Appointment).filter(
        models.Appointment.appointment_id == appointment_id
    ).first()


def get_all_appointments(db: Session, skip: int = 0, limit: int = 100) -> List[models.Appointment]:
    """Retrieve all appointments with pagination."""
    return db.query(models.Appointment).offset(skip).limit(limit).all()


def get_appointments_for_patient(db: Session, patient_id: int, skip: int = 0, limit: int = 100) -> List[models.Appointment]:
    """Retrieve all appointments for a specific patient."""
    return db.query(models.Appointment).filter(
        models.Appointment.patient_id == patient_id
    ).offset(skip).limit(limit).all()


def get_appointments_for_doctor(db: Session, doctor_id: int, skip: int = 0, limit: int = 100) -> List[models.Appointment]:
    """Retrieve all appointments for a specific doctor."""
    return db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor_id
    ).offset(skip).limit(limit).all()


def get_available_slots_in_a_day(db: Session, day: date) -> List[schemas.AvailableSlot]:
    """
    Get all available appointment slots for a given day.
    
    This function considers:
    - Working hours: 8:30 AM to 5:30 PM
    - Lunch break: 11:30 AM to 1:30 PM
    - Existing appointments
    - Available doctors
    """
    # Define working hours and lunch break
    start_of_day = datetime.combine(day, time(8, 30))
    end_of_day = datetime.combine(day, time(17, 30))
    lunch_start = time(11, 30)
    lunch_end = time(13, 30)
    slot_duration = timedelta(hours=1)

    # Get all doctors and existing appointments for the day
    doctors = db.query(models.Doctor).all()
    appointments = db.query(models.Appointment).filter(
        models.Appointment.appointment_day == day
    ).all()
    
    # Create set of taken appointment slots
    taken_slots = set((appt.doctor_id, appt.appointment_time) for appt in appointments)

    # Generate available slots
    available_slots: List[schemas.AvailableSlot] = []
    current_time = start_of_day

    while current_time + slot_duration <= end_of_day:
        # Skip lunch break
        if lunch_start <= current_time.time() < lunch_end:
            current_time += slot_duration
            continue

        # Find doctors available at this time
        free_doctors = [
            schemas.AvailableDoctor(
                doctor_id=getattr(doctor, 'doctor_id'),
                doctor_name=getattr(doctor, 'doctor_name')
            )
            for doctor in doctors
            if (getattr(doctor, 'doctor_id'), current_time.time()) not in taken_slots
        ]

        # Add slot if there are available doctors
        if free_doctors:
            available_slots.append(
                schemas.AvailableSlot(
                    datetime=current_time,
                    available_doctors=free_doctors
                )
            )

        current_time += slot_duration

    return available_slots


def update_appointment(db: Session, appointment_id: int, appointment_update: schemas.AppointmentUpdate) -> Optional[models.Appointment]:
    """Update an existing appointment."""
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
    
    update_data = appointment_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_appointment, key, value)
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def delete_appointment(db: Session, appointment_id: int) -> Optional[models.Appointment]:
    """Delete an appointment."""
    db_appointment = get_appointment(db, appointment_id)
    if not db_appointment:
        return None
    
    db.delete(db_appointment)
    db.commit()
    return db_appointment

# ============================================================================
# DOCTOR CRUD OPERATIONS
# ============================================================================

def get_doctor(db: Session, doctor_id: int) -> Optional[models.Doctor]:
    """Retrieve a doctor by doctor ID."""
    return db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()


def get_doctors(db: Session, skip: int = 0, limit: int = 100) -> List[models.Doctor]:
    """Retrieve all doctors with pagination."""
    return db.query(models.Doctor).offset(skip).limit(limit).all()


def create_doctor(db: Session, doctor_in: schemas.DoctorCreate, creator_id: int) -> models.Doctor:
    """Create a new doctor record."""
    db_doctor = models.Doctor(
        doctor_id=doctor_in.doctor_id,
        doctor_name=doctor_in.doctor_name,
        major=doctor_in.major or "General Medicine",
        hospital_id=doctor_in.hospital_id,
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def update_doctor(db: Session, doctor_id: int, doctor_update: schemas.DoctorUpdate) -> Optional[models.Doctor]:
    """Update an existing doctor's information."""
    db_doctor = get_doctor(db, doctor_id=doctor_id)
    if not db_doctor:
        return None

    update_data = doctor_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_doctor, key, value)

    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def delete_doctor(db: Session, doctor_id: int) -> Optional[models.Doctor]:
    """Delete a doctor record."""
    db_doctor = get_doctor(db, doctor_id=doctor_id)
    if not db_doctor:
        return None
    
    db.delete(db_doctor)
    db.commit()
    return db_doctor


# ============================================================================
# HOSPITAL CRUD OPERATIONS
# ============================================================================

def get_hospital(db: Session, hospital_id: int) -> Optional[models.Hospital]:
    """Retrieve a hospital by hospital ID."""
    return db.query(models.Hospital).filter(models.Hospital.hospital_id == hospital_id).first()


def get_hospitals(db: Session, skip: int = 0, limit: int = 100) -> List[models.Hospital]:
    """Retrieve all hospitals with pagination."""
    return db.query(models.Hospital).offset(skip).limit(limit).all()


def create_hospital(db: Session, hospital_in: schemas.HospitalCreate) -> models.Hospital:
    """Create a new hospital record."""
    db_hospital = models.Hospital(**hospital_in.model_dump())
    db.add(db_hospital)
    db.commit()
    db.refresh(db_hospital)
    return db_hospital


def update_hospital(db: Session, hospital_id: int, hospital_update: schemas.HospitalUpdate) -> Optional[models.Hospital]:
    """Update an existing hospital's information."""
    db_hospital = get_hospital(db, hospital_id=hospital_id)
    if not db_hospital:
        return None

    update_data = hospital_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_hospital, key, value)

    db.commit()
    db.refresh(db_hospital)
    return db_hospital


def delete_hospital(db: Session, hospital_id: int) -> Optional[models.Hospital]:
    """Delete a hospital record."""
    db_hospital = get_hospital(db, hospital_id=hospital_id)
    if not db_hospital:
        return None
    
    db.delete(db_hospital)
    db.commit()
    return db_hospital


# ============================================================================
# CHAT MESSAGE CRUD OPERATIONS
# ============================================================================

def create_chat_message(db: Session, message: schemas.ChatMessageCreate, user_id: Optional[int] = None) -> models.ChatMessage:
    """
    Create a new chat message.
    
    This function saves user messages to the database. Chatbot responses
    can be handled synchronously or asynchronously depending on implementation.
    """
    db_message = models.ChatMessage(**message.model_dump(), user_id=user_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_chat_message(db: Session, message_id: int) -> Optional[models.ChatMessage]:
    """Retrieve a chat message by message ID."""
    return db.query(models.ChatMessage).filter(models.ChatMessage.chat_id == message_id).first()


def get_chat_messages_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.ChatMessage]:
    """
    Retrieve chat messages for a specific user.
    
    This fetches messages initiated by or involving the user, ordered by
    most recent first. The exact filter depends on conversation structure.
    """
    return db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == user_id
    ).order_by(
        models.ChatMessage.time_stamp.desc()
    ).offset(skip).limit(limit).all()

# ============================================================================
# MEDICAL REPORT CRUD OPERATIONS
# ============================================================================

def create_medical_report(db: Session, report: schemas.MedicalReportCreate) -> models.MedicalReport:
    """Create a new medical report."""
    db_report = models.MedicalReport(**report.model_dump())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_medical_report(db: Session, record_id: int) -> Optional[models.MedicalReport]:
    """Retrieve a medical report by record ID."""
    return db.query(models.MedicalReport).filter(models.MedicalReport.record_id == record_id).first()


def get_medical_reports_for_patient(db: Session, patient_id: int, skip: int = 0, limit: int = 100) -> List[models.MedicalReport]:
    """Retrieve all medical reports for a specific patient, ordered by date."""
    return (
        db.query(models.MedicalReport)
        .filter(models.MedicalReport.patient_id == patient_id)
        .order_by(models.MedicalReport.in_day.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_medical_report(db: Session, record_id: int, report_update: schemas.MedicalReportUpdate) -> Optional[models.MedicalReport]:
    """Update an existing medical report."""
    db_report = get_medical_report(db, record_id)
    if not db_report:
        return None
    
    update_data = report_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)
    
    db.commit()
    db.refresh(db_report)
    return db_report


def delete_medical_report(db: Session, record_id: int) -> Optional[models.MedicalReport]:
    """Delete a medical report."""
    db_report = get_medical_report(db, record_id)
    if not db_report:
        return None
    
    db.delete(db_report)
    db.commit()
    return db_report


# ============================================================================
# FUTURE ENHANCEMENTS (Placeholder Functions)
# ============================================================================

# TODO: Implement conversation management for chat messages
# def get_conversation_messages(db: Session, conversation_id: int, skip: int = 0, limit: int = 100):
#     """Retrieve all messages in a conversation."""
#     pass

# TODO: Implement chatbot response handling
# def add_chatbot_response_to_message(db: Session, message_id: int, response_text: str):
#     """Add a chatbot response to an existing message."""
#     db_message = get_chat_message(db, message_id)
#     if db_message:
#         db_message.response = response_text
#         db.commit()
#         db.refresh(db_message)
#     return db_message